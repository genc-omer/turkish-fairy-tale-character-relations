# -*- coding: utf-8 -*-
"""
run_baseline.py — batch runner without the GUI.

Purpose: repeat the CALL ORDER of mainwindow.Ui_MainWindow.analiz_et exactly, without
the GUI, and write the character + relation predictions for each tale to
predictions.json.

This file does not change the pipeline: it only imports analizClass and iliskiClass
and runs them in the same order as the GUI.

analiz_et flow (mainwindow.py, Ui_MainWindow.analiz_et):
    analiz = MetinAnaliz(hikaye_yolu)
    sirali_gruplar = analiz.tum_islemler()        # -> writes karakterler.txt (>=4 mentions)
    self.iliski.story_path = hikaye_yolu
    self.iliski.load_text()                        # reads karakterler.txt
    self.iliski.split_sentence_dialog()
    self.iliski.process()                          # -> self.iliski.all_relations

Dominant relation: the calculation inside iliskiClass.overall_relation_graph is
replicated ONE-TO-ONE (without touching the class, by reading all_relations).
"""

import argparse
import io
import json
import os
import sys
import traceback
from collections import Counter, defaultdict
from contextlib import redirect_stdout

# The Windows console may be cp1252; switch stdout/stderr to UTF-8 for Turkish characters.
for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8")
    except Exception:
        pass

# This file is inside proje/. Pin the CWD here so that:
#  - the imports (analizClass/iliskiClass) resolve
#  - MetinAnaliz.tum_islemler writes "karakterler.txt" to the CWD (hardcoded relative)
#  - CharacterRelations.load_text reads "karakterler.txt" from the CWD
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from analizClass import MENTION_THRESHOLD, MetinAnaliz   # noqa: E402
from iliskiClass import CharacterRelations    # noqa: E402

HIKAYE_DIR = os.path.join(SCRIPT_DIR, "NLP-Hikayeler", "hikayeler")
KARAKTERLER_TXT = os.path.join(SCRIPT_DIR, "karakterler.txt")


def map_emotion(label):
    """Map savasy labels to the gold vocabulary (pozitif/negatif/notr).

    savasy/bert-base-turkish-sentiment-cased returns 'positive'/'negative'
    in practice. An unknown label is left as is (so that it stays visible).
    """
    if label is None:
        return "notr"
    l = str(label).strip().lower()
    if l.startswith("pos") or l in ("olumlu", "pozitif"):
        return "pozitif"
    if l.startswith("neg") or l in ("olumsuz", "negatif"):
        return "negatif"
    if l.startswith("neu") or l in ("notr", "nötr", "neutral"):
        return "notr"
    return l  # unknown -> keep the raw label


def dominant_from_relations(all_relations):
    """ONE-TO-ONE the same as iliskiClass.overall_relation_graph:
    one dominant emotion per pair via undirected sorted pair + Counter.most_common."""
    relations_emotions = defaultdict(list)
    for relation in all_relations:
        c1, c2 = sorted([relation["from"], relation["to"]])
        relations_emotions[(c1, c2)].append(relation["emotion"])

    out = []
    raw_dominant = {}
    for pair, emotions in relations_emotions.items():
        counts = Counter(emotions)
        dominant_emotion = counts.most_common(1)[0][0]  # same tie-break as the graph
        raw_dominant[pair] = dominant_emotion
        out.append({"from": pair[0], "to": pair[1], "type": map_emotion(dominant_emotion)})
    return out, raw_dominant


def read_karakterler_txt(path=KARAKTERLER_TXT):
    """karakterler.txt written by MetinAnaliz: 'kanonik,var1,var2,...' (>=4 mentions)."""
    spans = {}
    if not os.path.exists(path):
        return spans
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split(",") if p.strip()]
            if parts:
                spans[parts[0]] = parts
    return spans


def reset_iliski(iliski):
    """Same state reset as Ui_MainWindow.geri_git in the GUI.
    self.iliski is built once in the GUI and reset between tales."""
    iliski.story_path = None
    iliski.variation_to_character = {}
    iliski.text = ""
    iliski.segments = []
    iliski.all_relations = []
    iliski.past_sentences = []
    iliski.is_dialog = False  # defensive (process already sets it per segment)


def run_one(story_path, iliski, verbose_logs=False):
    """Repeat the analiz_et flow for one tale and return the predictions as a dict."""
    story_file = os.path.basename(story_path)
    result = {"story_file": story_file}

    # ---- STAGE 1: Character detection (analiz_et: a NEW MetinAnaliz for each tale) ----
    analiz = MetinAnaliz(story_path)
    log1 = io.StringIO()
    with redirect_stdout(log1):
        sirali = analiz.tum_islemler()  # writes karakterler.txt; returns [(isim,sayı),...] (>=4 mentions)

    raw_detected = sorted(analiz.characters)              # (a) ALL detections (before filtering, raw)
    final_chars = [name for (name, cnt) in sirali]        # (b) MAIN (past the >=4 threshold, merged)
    final_counts = {name: cnt for (name, cnt) in sirali}
    spans = read_karakterler_txt()                        # >=4 canonical -> variants

    # ---- STAGE 2: Relation extraction (analiz_et: self.iliski is reused) ----
    reset_iliski(iliski)
    iliski.story_path = story_path
    log2 = io.StringIO()
    with redirect_stdout(log2):
        iliski.load_text()              # reads karakterler.txt (STAGE 1 output)
        iliski.split_sentence_dialog()
        iliski.process()                # fills self.iliski.all_relations

    relations, raw_dominant = dominant_from_relations(iliski.all_relations)
    raw_label_tally = Counter(r["emotion"] for r in iliski.all_relations)

    # Classifier exception audit: the process() output stayed buried in log2; send the classifier
    # exception warnings to a visible channel (stderr + _diag).
    classifier_uyarilar = [ln.strip() for ln in log2.getvalue().splitlines() if "[uyari]" in ln]
    for ln in classifier_uyarilar:
        print(f"  !! {story_file} | {ln}", file=sys.stderr)

    # Diagnostic instrumentation: CHRONOLOGICAL raw label sequence per pair.
    # Written only to _diag so that recency/final-state aggregation experiments can be
    # computed offline; does not touch the SCORED "relations" field.
    pair_sequences = defaultdict(list)
    for rel in iliski.all_relations:
        c1, c2 = sorted([rel["from"], rel["to"]])
        pair_sequences[(c1, c2)].append(rel["emotion"])

    # ---- Schema: the merged final list (≥4 mentions) = the model's CHARACTER prediction.
    #      Both the "tüm" and the "ana" metric are computed from this single list.
    #      The raw (pre-filter) list is NOT SCORED; it stays only in _diag as a reference. ----
    result["characters"] = final_chars             # merged final list, ≥4 mentions (sorted DESCENDING by mention count)
    result["character_counts"] = final_counts      # {kanonik: geçiş_sayısı}, used for the main = top-N selection
    result["relations"] = relations                # [{from,to,type}], type ∈ {pozitif,negatif}

    # ---- Diagnostics/transparency (NOT SCORED, reference only) ----
    result["_diag"] = {
        "raw_detected": raw_detected,              # (a) raw detections (before filtering), NOT SCORED
        "n_raw_detected": len(raw_detected),
        "n_final_ge5": len(final_chars),
        "final_spans": spans,
        "threshold": MENTION_THRESHOLD,            # mention threshold of analizClass (fixed, not adaptive)
        "n_segments": len(iliski.segments),
        "n_all_relations": len(iliski.all_relations),
        "n_dominant_pairs": len(relations),
        "raw_emotion_labels": dict(raw_label_tally),
        # chronological raw label sequences (for offline recency aggregation)
        "pair_sequences": {f"{a}||{b}": v for (a, b), v in pair_sequences.items()},
        # classifier exception audit record (per tale)
        "classifier_uyarilar": classifier_uyarilar,
    }

    if verbose_logs:
        result["_logs"] = {"analiz_stdout": log1.getvalue(), "iliski_stdout": log2.getvalue()}

    return result


def print_summary(res):
    d = res["_diag"]
    raw = d.get("raw_detected", [])
    print(f"\n===== MASAL: {res['story_file']} =====")
    print(f"[ham] tespit (filtre öncesi, SKORLANMAZ) — {d['n_raw_detected']} adet:")
    print("    " + (", ".join(raw) if raw else "(yok)"))
    print(f"[PRED] KARAKTER tahmini = ≥{MENTION_THRESHOLD} merged final — {d['n_final_ge5']} adet:")
    if res["characters"]:
        for name in res["characters"]:
            print(f"    - {name} ({res['character_counts'].get(name)} geçiş)")
    else:
        print("    (yok)")
    if d["final_spans"]:
        print("    karakterler.txt (kanonik <- varyasyonlar):")
        for canon, parts in d["final_spans"].items():
            variants = [p for p in parts if p != canon]
            print(f"      {canon} <- {', '.join(variants) if variants else '(varyasyon yok)'}")
    print(f"[rel] segment={d['n_segments']} | all_relations={d['n_all_relations']} "
          f"| ham duygu etiketleri={d['raw_emotion_labels']}")
    print(f"[rel] Baskın ilişkiler (çift başına tek) — {d['n_dominant_pairs']} adet:")
    if res["relations"]:
        for r in res["relations"]:
            print(f"      {r['from']} -- {r['to']} : {r['type']}")
    else:
        print("      (yok)")


def main():
    ap = argparse.ArgumentParser(description="GUI'siz baseline runner (FAZ 1)")
    ap.add_argument("--stories", nargs="*", default=None,
                    help="Çalıştırılacak masal dosya adları (HIKAYE_DIR içinde). "
                         "Verilmezse tüm *.txt.")
    ap.add_argument("--out", default="predictions.json",
                    help="Çıktı JSON (SCRIPT_DIR'e göreli ya da mutlak).")
    ap.add_argument("--verbose-logs", action="store_true",
                    help="Pipeline stdout'unu JSON'a da gömer.")
    args = ap.parse_args()

    if args.stories:
        story_files = list(args.stories)
        missing = [s for s in story_files if not os.path.exists(os.path.join(HIKAYE_DIR, s))]
        if missing:
            print(f"HATA: bulunamayan masal dosyaları: {missing}", file=sys.stderr)
            print(f"HIKAYE_DIR: {HIKAYE_DIR}", file=sys.stderr)
            sys.exit(1)
    else:
        story_files = sorted(f for f in os.listdir(HIKAYE_DIR) if f.lower().endswith(".txt"))

    out_path = args.out if os.path.isabs(args.out) else os.path.join(SCRIPT_DIR, args.out)

    print(f"CWD            : {os.getcwd()}")
    print(f"HIKAYE_DIR     : {HIKAYE_DIR}")
    print(f"Çıktı          : {out_path}")
    print(f"Masal sayısı   : {len(story_files)}")
    print(f"Masallar       : {story_files}")
    print("\nCharacterRelations bir kez kuruluyor (modeller bir kez yükleniyor)...")
    iliski_log = io.StringIO()
    with redirect_stdout(iliski_log):
        iliski = CharacterRelations(story_path=None)  # same as in mainwindow.setupUi
    print("  ... CharacterRelations hazır (spaCy tr_core_news_trf + savasy yüklendi).")

    predictions = []
    for i, sf in enumerate(story_files, 1):
        story_path = os.path.join(HIKAYE_DIR, sf)
        print(f"\n[{i}/{len(story_files)}] İşleniyor: {sf}")
        try:
            res = run_one(story_path, iliski, verbose_logs=args.verbose_logs)
            predictions.append(res)
            print_summary(res)
        except Exception:
            err = traceback.format_exc()
            print(f"  !! HATA ({sf}):\n{err}", file=sys.stderr)
            predictions.append({"story_file": sf, "error": err})

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)

    ok = sum(1 for p in predictions if "error" not in p)
    print(f"\n==== BİTTİ: {ok}/{len(predictions)} masal başarılı -> {out_path} ====")
    # Audit counter: total classifier exceptions over all tales
    toplam_uyari = sum(len(p.get("_diag", {}).get("classifier_uyarilar", []))
                       for p in predictions if "error" not in p)
    print(f"==== KALEM-4 denetim: toplam classifier exception = {toplam_uyari} ====")


if __name__ == "__main__":
    main()
