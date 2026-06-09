# -*- coding: utf-8 -*-
"""
evaluation.py — FAZ 2: predictions.json'u gold (test_data/annotations/*.json)
karşısında değerlendirir, "before" metriklerini üretir.

YALNIZCA okuma yapar: predictions.json + gold JSON'ları. Pipeline dosyalarına
(analizClass/iliskiClass/...) DOKUNMAZ.

═══════════ YÖNTEM (onaylanan eşleme) ═══════════

DOSYA EŞLEME: ad normalizasyonu (boşluk+altçizgi+uzantı sil, küçük harf) ile
  prediction.story_file ↔ gold dosya adı / gold['story'] / gold['text_file'].

KARAKTER EŞLEME (1-e-1, maksimum bipartite — Kuhn, deterministik):
  - Tahmin ismi gold KANONİK veya char_spans VARYASYONLARINA uyarsa aday kenar
    (norm: küçük harf + boşluk sıkıştır; difflib cutoff=0.8 fallback).
  - Bir tahmin ↔ en fazla bir gold; bir gold ↔ en fazla bir tahmin.
  - Eşleşmeyen tahmin = FP karakter; eşleşmeyen gold = FN karakter.
  - Tüm karakter: tahmin = final ≥5 liste ↔ gold['characters'].
  - Ana karakter: tahmin = final listenin geçiş_sayısı TOP-N'i (N=len(gold.main),
    deterministik tie-break: (-sayı, isim)) ↔ gold['main_characters'].
    NOT (proxy uyarısı): #tahmin == #gold == N olduğunda matematiksel olarak
    precision@N = recall@N = F1@N. Geçen senenin tam ana-tahmin yöntemi belirsiz
    olduğundan ana-F1 onların %90,8'iyle BİREBİR kıyaslanamaz; anlamlı sayı
    before/after DELTASIdır (aynı yöntemle). Mutlak kıyas yaklaşıktır.

İLİŞKİ DEĞERLENDİRMESİ (karakterle AYNI 1-e-1 haritayı paylaşır):
  - Tüm-karakter eşleşmesinden matched_map {tahmin_ismi: gold_kanonik}.
  - Her tahmin ilişkisi (from,to) bu haritadan gold-uzayına çevrilir.
    * iki uç da eşleşmiş ve farklı gold → geçerli gold-uzayı kenarı (pred valans).
    * en az bir uç eşleşmemiş (FP karakter) VEYA aynı gold'a düşüyor → FP ilişki.
    Böylece bir gold karakter N parçaya bölündüyse (üvey anne→3), yalnız 1 parça
    gold'a eşleşir; diğer parçaların ilişkileri FP ilişki olur (Hansel "20 yanlış").
  - EDGE F1: gold'daki TÜM çiftler (notr DAHİL) üzerinden; valanstan bağımsız
    (çift bulunduysa TP). notr_handling'den ETKİLENMEZ.
  - POZ/NEG P/R/F1 + recall-oranı: notr_handling bayrağına tabi.
    * exclude (PRIMARY): gold-notr çiftleri poz/neg evreninden çıkarılır
      (poz/neg etiketlense bile FP sayılmaz) → geçen seneyle (2-sınıf gold) elma-elma.
    * strict: notr çiftler kalır (yanlış valans → FP).
    * edge_only: poz/neg için exclude ile aynı (notr yalnız edge F1'e katkı).

AGREGAT: Micro = TP/FP/FN havuzla, tek P/R/F1. Macro = masal-başı-F1 ortalaması
  (geçen seneyle aynı). Bir masalda bir poz/neg sınıfı gold'da hiç yoksa macro'da
  o masal için o sınıf ATLANIR (dokümante).

recall-oranı (geçen sene 67,1/48,9 ile birebir): havuzlanmış R_C = ΣTP_C/Σgold_C
  (exclude evreninde). Geçen senenin "51/76" tarzı.
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

FUZZY_CUTOFF = 0.85          # kural 3: yüksek bulanık benzerlik (sonek/yazım varyantı)
CONTAIN_MIN = 3              # kural 2 koruması: eşleşen gold-adı ≥3 karakter
HEAD_CUTOFF = 0.80           # kural 2 head-anchor: pred ile gold-form BAŞ kelime benzerliği eşiği

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)   # Türkçe harfler \w'de korunur


# ───────────────────────── yardımcılar ─────────────────────────

def norm(s):
    """küçük harf + noktalama temizle + iç boşlukları daralt."""
    s = _PUNCT_RE.sub(" ", str(s).strip().lower())
    return " ".join(s.split())


def file_key(name):
    """Dosya/story adı normalizasyonu: uzantı + boşluk + altçizgi sil, küçük harf."""
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
    """gold kanonik + char_spans varyasyonları (normalize)."""
    return [norm(f) for f in ([gold_char] + list(spans_map.get(gold_char, [])))]


def _tier_exact(npred, nforms):
    """Kural 1: tam eşleşme (normalize sonrası)."""
    return npred in nforms


def _head(s):
    """Türkçe head-final: baş kelime = son token."""
    toks = s.split()
    return toks[-1] if toks else s


def _head_match(npred, f):
    """pred ile gold-form BAŞ kelimesi aynı/sonek-varyantı mı.
    'baba'~'babası' (0.80) ve 'oduncu'~'oduncu' (1.0) kabul;
    'kral'~'kraliçe' (0.73), 'kızı'~'kral', 'delikanlı'~'babası' RED."""
    return difflib.SequenceMatcher(None, _head(npred), _head(f)).ratio() >= HEAD_CUTOFF


def _tier_contain(npred, nforms):
    """Kural 2: içerme (çift yönlü substring) + eşleşen gold-adı ≥3 karakter +
    HEAD-ANCHORED: pred ile gold-form BAŞ kelimesi eşleşmeli. Bu, sahiplik/ön-kelime
    eşleşmelerini engeller ('hansel gretel'in babası'→Hansel, 'kralın kızı'→Kral)."""
    for f in nforms:
        if len(f) >= CONTAIN_MIN and (f in npred or (len(npred) >= CONTAIN_MIN and npred in f)):
            if _head_match(npred, f):
                return True
    return False


def _tier_fuzzy(npred, nforms):
    """Kural 3: yüksek bulanık benzerlik (difflib ≥ 0.85)."""
    return bool(difflib.get_close_matches(npred, nforms, n=1, cutoff=FUZZY_CUTOFF))


_TIERS = (("exact", _tier_exact), ("contain", _tier_contain), ("fuzzy", _tier_fuzzy))


def _kuhn(free_preds, free_golds, elig):
    """Maksimum kardinalite bipartite eşleme (Kuhn). free_preds verilen sırada
    işlenir (deterministik). elig(i, j) -> bool. Döner: {pred_idx: gold_idx}."""
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
    """KADEMELİ 1-e-1 eşleme: exact → contain(≥3) → fuzzy(≥0.85).
    Her kademe önceki eşleşmeleri KİLİTLER (yeniden yönlendirmez) → güçlü kanıt
    (exact) zayıf kanıttan (contain/fuzzy) önce gelir; böylece 'sülün kız'ın
    yanlışlıkla 'Sülün Kızın Babası'na takas edilmesi gibi hatalar önlenir.
    Bir gold N parçaya bölündüyse yine SADECE bir parça eşleşir (TP), diğerleri
    FP kalır → alias bölünmesinin precision etkisi (Odak 3) korunur.
    Döner: {pred_idx: (gold_idx, tier)}."""
    nforms = [_forms(g, spans_map) for g in golds]
    npreds = [norm(p) for p in preds]
    matched = {}
    used_p, used_g = set(), set()
    for tier_name, tier_fn in _TIERS:
        free_p = [i for i in range(len(preds)) if i not in used_p]   # verilen sıra (sayıya göre azalan)
        free_g = [j for j in range(len(golds)) if j not in used_g]
        m = _kuhn(free_p, free_g, lambda i, j: tier_fn(npreds[i], nforms[j]))
        for p, g in m.items():
            matched[p] = (g, tier_name)
            used_p.add(p)
            used_g.add(g)
    return matched


def pair_key(a, b):
    return tuple(sorted([norm(a), norm(b)]))


# ───────────────────────── tek masal değerlendirme ─────────────────────────

def eval_story(pred, gold):
    """Bir masal için tüm sayımları döndürür (karakter + ilişki + valans evreni)."""
    out = {"story_file": pred.get("story_file"), "gold_story": gold.get("story")}

    pred_chars = list(pred.get("characters", []))          # ≥5 final (sayıya göre azalan)
    counts = pred.get("character_counts", {}) or {}
    gold_chars = list(gold.get("characters", []))
    gold_main = list(gold.get("main_characters", []))
    spans = gold.get("char_spans", {}) or {}

    # ---- TÜM KARAKTER ----
    p2g = match_characters(pred_chars, gold_chars, spans)   # {pred_idx:(gold_idx,tier)}
    tp_all = len(p2g)
    fp_all = len(pred_chars) - tp_all
    fn_all = len(gold_chars) - tp_all
    out["char_all"] = {"tp": tp_all, "fp": fp_all, "fn": fn_all}
    # ilişki için matched_map: tahmin_ismi -> gold_kanonik (TÜM eşleşmesinden)
    matched_map = {pred_chars[i]: gold_chars[g] for i, (g, _t) in p2g.items()}
    # eşleşme detayları (sağlık kontrolü için)
    out["matches"] = [{"pred": pred_chars[i], "gold": gold_chars[g], "tier": t}
                      for i, (g, t) in sorted(p2g.items())]
    matched_gold = {g for (g, _t) in p2g.values()}
    out["fp_chars"] = [pred_chars[i] for i in range(len(pred_chars)) if i not in p2g]
    out["fn_chars"] = [gold_chars[j] for j in range(len(gold_chars)) if j not in matched_gold]

    # ---- ANA KARAKTER (top-N proxy) ----
    N = len(gold_main)
    # deterministik: sayıya göre azalan, eşitlikte isim artan; final liste zaten azalan
    pred_sorted = sorted(pred_chars, key=lambda c: (-counts.get(c, 0), c))
    topN = pred_sorted[:N] if N <= len(pred_sorted) else pred_sorted[:]
    p2g_main = match_characters(topN, gold_main, spans)
    tp_m = len(p2g_main)
    fp_m = len(topN) - tp_m
    fn_m = len(gold_main) - tp_m
    out["char_main"] = {"tp": tp_m, "fp": fp_m, "fn": fn_m,
                        "N": N, "n_pred_topN": len(topN)}

    # ---- İLİŞKİ: gold-uzayına çevir ----
    gold_edges = {}                       # pair_key -> gold type (pozitif/negatif/notr)
    for r in gold.get("relations", []):
        gold_edges[pair_key(r["from"], r["to"])] = norm(r["type"])

    pred_edges = {}                       # pair_key -> pred type (gold-uzayı, geçerli)
    spurious_types = []                   # FP-karakter / self-loop kenarlarının pred valansı
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
    fp_e = len(pset - gset) + len(spurious_types)   # gold'da olmayan + FP-karakter kenarları
    fn_e = len(gset - pset)
    out["edge"] = {"tp": tp_e, "fp": fp_e, "fn": fn_e,
                   "n_gold_pairs": len(gset), "n_gold_notr": sum(1 for t in gold_edges.values() if t == "notr")}

    # ---- VALANS evreni: (gold_type, pred_type) tuple listesi ----
    universe = []
    for k in (gset | pset):
        universe.append((gold_edges.get(k), pred_edges.get(k)))   # None = yok
    for t in spurious_types:
        universe.append((None, t))                                # pred-only (FP)
    out["valence_universe"] = universe
    return out


# ───────────────────────── valans sınıf metrikleri ─────────────────────────

def class_counts(universe, cls, mode):
    """Tek sınıf (pozitif/negatif) için bir masaldan TP/FP/FN (notr_handling: mode)."""
    tp = fp = fn = 0
    gold_has = 0
    for gold_t, pred_t in universe:
        if mode in ("exclude", "edge_only") and gold_t == "notr":
            continue                      # poz/neg evreninden çıkar
        if gold_t == cls:
            gold_has += 1
            if pred_t == cls:
                tp += 1
            else:
                fn += 1
        else:
            if pred_t == cls:
                fp += 1                   # gold farklı/yok/notr(strict) ama pred==cls
    return tp, fp, fn, gold_has


# ───────────────────────── agregat ─────────────────────────

def aggregate(per_story, getter):
    """getter(story)->(tp,fp,fn). Micro (havuz) + Macro (masal-F1 ort) döndürür."""
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
    """Poz/neg sınıfı için micro + macro (boş sınıflı masalları macro'da atla)."""
    TP = FP = FN = 0
    f1s = []
    for s in per_story:
        tp, fp, fn, gold_has = class_counts(s["valence_universe"], cls, mode)
        TP += tp; FP += fp; FN += fn
        if gold_has > 0:                  # macro'da yalnız o sınıf gold'da varsa say
            _, _, f = prf(tp, fp, fn)
            f1s.append(f)
    micro = prf(TP, FP, FN)
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0
    return {"micro_p": micro[0], "micro_r": micro[1], "micro_f1": micro[2],
            "macro_f1": macro_f1, "TP": TP, "FP": FP, "FN": FN,
            "recall_orani": (TP / (TP + FN) if (TP + FN) else 0.0),
            "recall_pay": TP, "recall_payda": TP + FN, "n_story_with_class": len(f1s)}


# ───────────────────────── ana ─────────────────────────

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

    # agregatlar
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

    # ── okunabilir tablo ──
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
