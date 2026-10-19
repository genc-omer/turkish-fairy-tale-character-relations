# -*- coding: utf-8 -*-
"""
evaluation.py — FAZ 2: evaluates predictions.json against the gold
(test_data/annotations/*.json) and produces the "before" metrics.

ONLY reads: predictions.json + the gold JSON files. Does NOT TOUCH the pipeline
files (analizClass/iliskiClass/...).

═══════════ METHOD (approved matching) ═══════════

FILE MATCHING: by name normalization (remove spaces + underscores + extension,
  lowercase): prediction.story_file ↔ gold file name / gold['story'] / gold['text_file'].

CHARACTER MATCHING (one-to-one, maximum bipartite — Kuhn, deterministic):
  - A predicted name that fits the gold CANONICAL name or a char_spans VARIANT
    is a candidate edge (norm: lowercase + collapse spaces; difflib cutoff=0.8 fallback).
  - One prediction ↔ at most one gold; one gold ↔ at most one prediction.
  - Unmatched prediction = FP character; unmatched gold = FN character.
  - All characters: prediction = final ≥5 list ↔ gold['characters'].
  - Main characters: prediction = TOP-N of the final list by geçiş_sayısı
    (N=len(gold.main), deterministic tie-break: (-count, name)) ↔ gold['main_characters'].
    NOTE (proxy warning): when #pred == #gold == N, mathematically
    precision@N = recall@N = F1@N. Since last year's exact main-prediction method is
    unclear, main-F1 cannot be compared ONE-TO-ONE with their 90.8%; the meaningful
    number is the before/after DELTA (same method). The absolute comparison is approximate.

RELATION EVALUATION (shares the SAME one-to-one map as characters):
  - matched_map {predicted_name: gold_canonical} from the all-character matching.
  - Each predicted relation (from,to) is mapped into gold space with this map.
    * both ends matched and different gold → valid gold-space edge (pred valence).
    * at least one end unmatched (FP character) OR both fall on the same gold → FP relation.
    So if a gold character is split into N pieces (üvey anne→3), only 1 piece
    matches the gold; the relations of the other pieces become FP relations (Hansel "20 wrong").
  - EDGE F1: over ALL gold pairs (INCLUDING notr); independent of valence
    (TP if the pair is found). NOT AFFECTED by notr_handling.
  - POZ/NEG P/R/F1 + recall rate: depend on the notr_handling flag.
    * exclude (PRIMARY): gold-notr pairs are removed from the poz/neg universe
      (not counted as FP even if labeled poz/neg) → apples to apples with last year (2-class gold).
    * strict: notr pairs stay (wrong valence → FP).
    * edge_only: same as exclude for poz/neg (notr only contributes to edge F1).

AGGREGATE: Micro = pooled TP/FP/FN, a single P/R/F1. Macro = mean of per-tale F1
  (same as last year). If a poz/neg class does not occur in a tale's gold, that class
  is SKIPPED for that tale in macro (documented).

recall rate (one-to-one with last year's 67.1/48.9): pooled R_C = ΣTP_C/Σgold_C
  (in the exclude universe). Like last year's "51/76" style.
"""

import argparse
import difflib
import json
import os
import re
import sys
from collections import defaultdict

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PRED = os.path.join(SCRIPT_DIR, "predictions.json")
DEFAULT_ANN = os.path.join(SCRIPT_DIR, "test_data", "annotations")

FUZZY_CUTOFF = 0.85          # rule 3: high fuzzy similarity (suffix/spelling variant)
CONTAIN_MIN = 3              # rule 2 guard: matched gold name ≥3 characters
HEAD_CUTOFF = 0.80           # rule 2 head anchor: threshold for HEAD-word similarity between pred and gold form

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)   # Turkish letters are kept by \w


# ───────────────────────── helpers ─────────────────────────

def norm(s):
    """lowercase + strip punctuation + collapse inner spaces."""
    s = _PUNCT_RE.sub(" ", str(s).strip().lower())
    return " ".join(s.split())


def file_key(name):
    """File/story name normalization: remove extension + spaces + underscores, lowercase."""
    b = str(name).lower()
    for ext in (".json", ".txt"):
        if b.endswith(ext):
            b = b[: -len(ext)]
    return b.replace(" ", "").replace("_", "")


def prf(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def _forms(gold_char, spans_map):
    """gold canonical name + char_spans variants (normalized)."""
    return [norm(f) for f in ([gold_char] + list(spans_map.get(gold_char, [])))]


def _tier_exact(npred, nforms):
    """Rule 1: exact match (after normalization)."""
    return npred in nforms


def _head(s):
    """Turkish is head-final: head word = last token."""
    toks = s.split()
    return toks[-1] if toks else s


def _head_match(npred, f):
    """Is the HEAD word of pred and gold form the same / a suffix variant?
    'baba'~'babası' (0.80) and 'oduncu'~'oduncu' (1.0) accepted;
    'kral'~'kraliçe' (0.73), 'kızı'~'kral', 'delikanlı'~'babası' REJECTED."""
    return difflib.SequenceMatcher(None, _head(npred), _head(f)).ratio() >= HEAD_CUTOFF


def _tier_contain(npred, nforms):
    """Rule 2: containment (two-way substring) + matched gold name ≥3 characters +
    HEAD-ANCHORED: the HEAD words of pred and gold form must match. This blocks
    possessive/leading-word matches ('hansel gretel'in babası'→Hansel, 'kralın kızı'→Kral)."""
    for f in nforms:
        if len(f) >= CONTAIN_MIN and (f in npred or (len(npred) >= CONTAIN_MIN and npred in f)):
            if _head_match(npred, f):
                return True
    return False


def _tier_fuzzy(npred, nforms):
    """Rule 3: high fuzzy similarity (difflib ≥ 0.85)."""
    return bool(difflib.get_close_matches(npred, nforms, n=1, cutoff=FUZZY_CUTOFF))


_TIERS = (("exact", _tier_exact), ("contain", _tier_contain), ("fuzzy", _tier_fuzzy))


def _kuhn(free_preds, free_golds, elig):
    """Maximum-cardinality bipartite matching (Kuhn). free_preds are processed in
    the given order (deterministic). elig(i, j) -> bool. Returns: {pred_idx: gold_idx}."""
    adj = {i: [j for j in free_golds if elig(i, j)] for i in free_preds}
    match_g = {}  # gold_idx -> pred_idx

    def try_k(u, vis):
        for v in adj[u]:
            if v not in vis:
                vis.add(v)
                if v not in match_g or try_k(match_g[v], vis):
                    match_g[v] = u
                    return True
        return False

    for u in free_preds:
        try_k(u, set())
    return {p: g for g, p in match_g.items()}


def match_characters(preds, golds, spans_map):
    """TIERED one-to-one matching: exact → contain(≥3) → fuzzy(≥0.85).
    Each tier LOCKS the earlier matches (does not reroute them) → strong evidence
    (exact) comes before weak evidence (contain/fuzzy); this prevents errors such as
    'sülün kız' being swapped by mistake to 'Sülün Kızın Babası'.
    If a gold is split into N pieces, still ONLY one piece matches (TP), the others
    stay FP → the precision effect of alias splitting (Odak 3) is kept.
    Returns: {pred_idx: (gold_idx, tier)}."""
    nforms = [_forms(g, spans_map) for g in golds]
    npreds = [norm(p) for p in preds]
    matched = {}
    used_p, used_g = set(), set()
    for tier_name, tier_fn in _TIERS:
        free_p = [i for i in range(len(preds)) if i not in used_p]   # given order (descending by count)
        free_g = [j for j in range(len(golds)) if j not in used_g]
        m = _kuhn(free_p, free_g, lambda i, j: tier_fn(npreds[i], nforms[j]))
        for p, g in m.items():
            matched[p] = (g, tier_name)
            used_p.add(p)
            used_g.add(g)
    return matched


def pair_key(a, b):
    return tuple(sorted([norm(a), norm(b)]))


# ───────────────────────── single-tale evaluation ─────────────────────────

def eval_story(pred, gold):
    """Returns all counts for one tale (characters + relations + valence universe)."""
    out = {"story_file": pred.get("story_file"), "gold_story": gold.get("story")}

    pred_chars = list(pred.get("characters", []))          # ≥5 final (descending by count)
    counts = pred.get("character_counts", {}) or {}
    gold_chars = list(gold.get("characters", []))
    gold_main = list(gold.get("main_characters", []))
    spans = gold.get("char_spans", {}) or {}

    # ---- ALL CHARACTERS ----
    p2g = match_characters(pred_chars, gold_chars, spans)   # {pred_idx:(gold_idx,tier)}
    tp_all = len(p2g)
    fp_all = len(pred_chars) - tp_all
    fn_all = len(gold_chars) - tp_all
    out["char_all"] = {"tp": tp_all, "fp": fp_all, "fn": fn_all}
    # matched_map for relations: predicted_name -> gold_canonical (from the ALL matching)
    matched_map = {pred_chars[i]: gold_chars[g] for i, (g, _t) in p2g.items()}
    # match details (for sanity checks)
    out["matches"] = [{"pred": pred_chars[i], "gold": gold_chars[g], "tier": t}
                      for i, (g, t) in sorted(p2g.items())]
    matched_gold = {g for (g, _t) in p2g.values()}
    out["fp_chars"] = [pred_chars[i] for i in range(len(pred_chars)) if i not in p2g]
    out["fn_chars"] = [gold_chars[j] for j in range(len(gold_chars)) if j not in matched_gold]

    # ---- MAIN CHARACTERS (top-N proxy) ----
    N = len(gold_main)
    # deterministic: descending by count, ascending by name on ties; the final list is already descending
    pred_sorted = sorted(pred_chars, key=lambda c: (-counts.get(c, 0), c))
    topN = pred_sorted[:N] if N <= len(pred_sorted) else pred_sorted[:]
    p2g_main = match_characters(topN, gold_main, spans)
    tp_m = len(p2g_main)
    fp_m = len(topN) - tp_m
    fn_m = len(gold_main) - tp_m
    out["char_main"] = {"tp": tp_m, "fp": fp_m, "fn": fn_m,
                        "N": N, "n_pred_topN": len(topN)}

    # ---- RELATIONS: map into gold space ----
    gold_edges = {}                       # pair_key -> gold type (pozitif/negatif/notr)
    for r in gold.get("relations", []):
        gold_edges[pair_key(r["from"], r["to"])] = norm(r["type"])

    pred_edges = {}                       # pair_key -> pred type (gold space, valid)
    spurious_types = []                   # pred valence of FP-character / self-loop edges
    for r in pred.get("relations", []):
        a = matched_map.get(r["from"])
        b = matched_map.get(r["to"])
        if a is not None and b is not None and norm(a) != norm(b):
            k = pair_key(a, b)
            pred_edges.setdefault(k, norm(r["type"]))
        else:
            spurious_types.append(norm(r["type"]))

    gset = set(gold_edges.keys())
    pset = set(pred_edges.keys())
    tp_e = len(gset & pset)
    fp_e = len(pset - gset) + len(spurious_types)   # not in gold + FP-character edges
    fn_e = len(gset - pset)
    out["edge"] = {"tp": tp_e, "fp": fp_e, "fn": fn_e,
                   "n_gold_pairs": len(gset), "n_gold_notr": sum(1 for t in gold_edges.values() if t == "notr")}

    # ---- VALENCE universe: list of (gold_type, pred_type) tuples ----
    universe = []
    for k in (gset | pset):
        universe.append((gold_edges.get(k), pred_edges.get(k)))   # None = missing
    for t in spurious_types:
        universe.append((None, t))                                # pred-only (FP)
    out["valence_universe"] = universe
    return out


# ───────────────────────── valence class metrics ─────────────────────────

def class_counts(universe, cls, mode):
    """TP/FP/FN for one class (pozitif/negatif) in one tale (notr_handling: mode)."""
    tp = fp = fn = 0
    gold_has = 0
    for gold_t, pred_t in universe:
        if mode in ("exclude", "edge_only") and gold_t == "notr":
            continue                      # remove from the poz/neg universe
        if gold_t == cls:
            gold_has += 1
            if pred_t == cls:
                tp += 1
            else:
                fn += 1
        else:
            if pred_t == cls:
                fp += 1                   # gold different/missing/notr(strict) but pred==cls
    return tp, fp, fn, gold_has


# ───────────────────────── aggregate ─────────────────────────

def aggregate(per_story, getter):
    """getter(story)->(tp,fp,fn). Returns micro (pooled) + macro (mean per-tale F1)."""
    TP = FP = FN = 0
    f1s = []
    for s in per_story:
        tp, fp, fn = getter(s)
        TP += tp; FP += fp; FN += fn
        _, _, f = prf(tp, fp, fn)
        f1s.append(f)
    micro = prf(TP, FP, FN)
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0
    return {"micro_p": micro[0], "micro_r": micro[1], "micro_f1": micro[2],
            "macro_f1": macro_f1, "TP": TP, "FP": FP, "FN": FN}


def aggregate_class(per_story, cls, mode):
    """Micro + macro for a poz/neg class (skip tales without that class in macro)."""
    TP = FP = FN = 0
    f1s = []
    for s in per_story:
        tp, fp, fn, gold_has = class_counts(s["valence_universe"], cls, mode)
        TP += tp; FP += fp; FN += fn
        if gold_has > 0:                  # in macro, count only if the class is in the gold
            _, _, f = prf(tp, fp, fn)
            f1s.append(f)
    micro = prf(TP, FP, FN)
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0
    return {"micro_p": micro[0], "micro_r": micro[1], "micro_f1": micro[2],
            "macro_f1": macro_f1, "TP": TP, "FP": FP, "FN": FN,
            "recall_orani": (TP / (TP + FN) if (TP + FN) else 0.0),
            "recall_pay": TP, "recall_payda": TP + FN, "n_story_with_class": len(f1s)}


# ───────────────────────── main ─────────────────────────

def load_gold_index(ann_dir):
    idx = {}
    for fn in sorted(os.listdir(ann_dir)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(ann_dir, fn), encoding="utf-8") as f:
            g = json.load(f)
        for key in {file_key(fn), file_key(g.get("story", "")), file_key(g.get("text_file", ""))}:
            if key:
                idx[key] = g
    return idx


def pct(x):
    return f"{x*100:.1f}"


def main():
    ap = argparse.ArgumentParser(description="FAZ 2 — before/after evaluation")
    ap.add_argument("--predictions", default=DEFAULT_PRED)
    ap.add_argument("--annotations", default=DEFAULT_ANN)
    ap.add_argument("--out-json", default=os.path.join(SCRIPT_DIR, "before_metrics.json"))
    ap.add_argument("--out-txt", default=os.path.join(SCRIPT_DIR, "before_metrics.txt"))
    ap.add_argument("--label", default="before", help="rapor etiketi (before/after)")
    args = ap.parse_args()

    with open(args.predictions, encoding="utf-8") as f:
        preds = json.load(f)
    gold_idx = load_gold_index(args.annotations)

    per_story = []
    unmatched = []
    for pred in preds:
        if "error" in pred:
            unmatched.append((pred.get("story_file"), "PRED ERROR"))
            continue
        key = file_key(pred.get("story_file", ""))
        gold = gold_idx.get(key)
        if gold is None:
            unmatched.append((pred.get("story_file"), f"gold yok (key={key})"))
            continue
        per_story.append(eval_story(pred, gold))

    # aggregates
    agg_all = aggregate(per_story, lambda s: (s["char_all"]["tp"], s["char_all"]["fp"], s["char_all"]["fn"]))
    agg_main = aggregate(per_story, lambda s: (s["char_main"]["tp"], s["char_main"]["fp"], s["char_main"]["fn"]))
    agg_edge = aggregate(per_story, lambda s: (s["edge"]["tp"], s["edge"]["fp"], s["edge"]["fn"]))

    valence = {}
    for mode in ("exclude", "strict", "edge_only"):
        valence[mode] = {
            "pozitif": aggregate_class(per_story, "pozitif", mode),
            "negatif": aggregate_class(per_story, "negatif", mode),
        }

    # ── before_metrics.json ──
    result = {
        "label": args.label,
        "n_stories_evaluated": len(per_story),
        "unmatched": unmatched,
        "character": {"all": agg_all, "main": agg_main},
        "edge": agg_edge,
        "valence": valence,
        "per_story": [{
            "story_file": s["story_file"],
            "char_all": s["char_all"], "char_main": s["char_main"], "edge": s["edge"],
            "matches": s.get("matches"), "fp_chars": s.get("fp_chars"), "fn_chars": s.get("fn_chars"),
        } for s in per_story],
        "baseline_lastyear": {"ana_macro_f1": 0.908, "tum_macro_f1": 0.818,
                              "poz_recall": 0.671, "neg_recall": 0.489},
    }
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # ── readable table ──
    L = []
    L.append(f"=== {args.label.upper()} METRİKLERİ — {len(per_story)} masal ===")
    if unmatched:
        L.append(f"!! Eşleşmeyen: {unmatched}")
    L.append("")
    L.append("── KARAKTER TESPİTİ (masal başı) ──")
    L.append(f"{'masal':24} | ANA tp/fp/fn  F1   | TÜM tp/fp/fn  P    R    F1")
    L.append("-" * 78)
    for s in per_story:
        a = s["char_main"]; t = s["char_all"]
        _, _, af = prf(a["tp"], a["fp"], a["fn"])
        tp_, tr_, tf_ = prf(t["tp"], t["fp"], t["fn"])
        L.append(f"{s['story_file']:24} | {a['tp']:2}/{a['fp']:2}/{a['fn']:2}  {pct(af):>4} | "
                 f"{t['tp']:2}/{t['fp']:2}/{t['fn']:2}  {pct(tp_):>4} {pct(tr_):>4} {pct(tf_):>4}")
    L.append("-" * 78)
    L.append(f"{'MICRO':24} | {'':12} {pct(agg_main['micro_f1']):>4} | "
             f"{'':12} {pct(agg_all['micro_p']):>4} {pct(agg_all['micro_r']):>4} {pct(agg_all['micro_f1']):>4}")
    L.append(f"{'MACRO (manşet)':24} | {'':12} {pct(agg_main['macro_f1']):>4} | "
             f"{'':12} {'':4} {'':4} {pct(agg_all['macro_f1']):>4}")
    L.append("")
    L.append("── İLİŞKİ TESPİTİ (masal başı, poz/neg = notr_handling='exclude') ──")
    L.append(f"{'masal':24} | EDGE tp/fp/fn F1  | POZ P/R/F1        | NEG P/R/F1")
    L.append("-" * 86)
    for s in per_story:
        e = s["edge"]
        _, _, ef = prf(e["tp"], e["fp"], e["fn"])
        ptp, pfp, pfn, _ = class_counts(s["valence_universe"], "pozitif", "exclude")
        ntp, nfp, nfn, _ = class_counts(s["valence_universe"], "negatif", "exclude")
        pp, pr, pf = prf(ptp, pfp, pfn)
        npp, nr, nf = prf(ntp, nfp, nfn)
        L.append(f"{s['story_file']:24} | {e['tp']:2}/{e['fp']:2}/{e['fn']:2} {pct(ef):>4} | "
                 f"{pct(pp):>4}/{pct(pr):>4}/{pct(pf):>4} | {pct(npp):>4}/{pct(nr):>4}/{pct(nf):>4}")
    L.append("-" * 86)
    ex = valence["exclude"]
    L.append(f"{'MICRO':24} | {'':10} {pct(agg_edge['micro_f1']):>4} | "
             f"{pct(ex['pozitif']['micro_p']):>4}/{pct(ex['pozitif']['micro_r']):>4}/{pct(ex['pozitif']['micro_f1']):>4} | "
             f"{pct(ex['negatif']['micro_p']):>4}/{pct(ex['negatif']['micro_r']):>4}/{pct(ex['negatif']['micro_f1']):>4}")
    L.append(f"{'MACRO':24} | {'':10} {pct(agg_edge['macro_f1']):>4} | "
             f"{'F1=':>4}{pct(ex['pozitif']['macro_f1']):>4}     | {'F1=':>4}{pct(ex['negatif']['macro_f1']):>4}")
    L.append("")
    L.append("── notr_handling KARŞILAŞTIRMASI (poz/neg micro F1) ──")
    L.append(f"{'mod':12} | POZ microF1 | NEG microF1 | POZ recall-oranı | NEG recall-oranı")
    L.append("-" * 76)
    for mode in ("exclude", "strict", "edge_only"):
        v = valence[mode]
        L.append(f"{mode:12} | {pct(v['pozitif']['micro_f1']):>10} | {pct(v['negatif']['micro_f1']):>10} | "
                 f"{v['pozitif']['recall_pay']:>3}/{v['pozitif']['recall_payda']:<3}={pct(v['pozitif']['recall_orani']):>4} | "
                 f"{v['negatif']['recall_pay']:>3}/{v['negatif']['recall_payda']:<3}={pct(v['negatif']['recall_orani']):>4}")
    L.append("")
    L.append("── MANŞET vs GEÇEN YIL (macro F1 / recall-oranı; yaklaşık kıyas) ──")
    L.append(f"  Ana karakter  macro F1 : {pct(agg_main['macro_f1'])}   (geçen yıl 90,8)")
    L.append(f"  Tüm karakter  macro F1 : {pct(agg_all['macro_f1'])}   (geçen yıl 81,8)")
    L.append(f"  Pozitif recall-oranı   : {pct(ex['pozitif']['recall_orani'])}   (geçen yıl 67,1)")
    L.append(f"  Negatif recall-oranı   : {pct(ex['negatif']['recall_orani'])}   (geçen yıl 48,9)")
    L.append("  NOT: Ana-F1 top-N proxy (precision@N=recall@N=F1@N); geçen senenin tam")
    L.append("       ana-tahmin yöntemi belirsiz → mutlak kıyas yaklaşık, asıl sinyal DELTA.")

    table = "\n".join(L)
    print(table)
    with open(args.out_txt, "w", encoding="utf-8") as f:
        f.write(table + "\n")
    print(f"\n[yazıldı] {args.out_json}\n[yazıldı] {args.out_txt}")


if __name__ == "__main__":
    main()
