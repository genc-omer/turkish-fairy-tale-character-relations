#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHARACTER DETECTION — PER-TALE LaTeX TABLE GENERATOR (AUTOMATIC)
Produces per-tale tables + score summaries for main characters and all characters,
in the format of Tables 5.1–5.4 of the old report.

DIFFERENCE: This version does NOT fill in numbers MANUALLY; it computes them
AUTOMATICALLY from evaluation.py + gold. The methodology is ONE-TO-ONE with evaluation.py:
  - all  : the system's final character list (predictions.characters) vs gold.characters[]
           head-anchored one-to-one matching.
  - main : TOP-N of the final list by geçiş_sayısı (N=len(gold.main_characters)) vs
           gold.main_characters[]  (top-N proxy).
  doğru (TP)=matched, fazla (FP)=unmatched prediction, eksik (FN)=missed gold.
  toplam = doğru + eksik (automatic).

NOTE (main characters): since this is a top-N proxy, most tales get fazla=eksik and P=R=F1;
this is normal/honest (see the old report's methodology).

USAGE:
    python karakter_tablolari.py                         # default predictions_after_t4.json
    python karakter_tablolari.py > tablolar.tex
    python karakter_tablolari.py --predictions predictions_after_odak1.json
    python karakter_tablolari.py --dump-json per_story_sonuc.json   # also writes the intermediate numbers
Needed in LaTeX: \\usepackage{float}  (tables are placed with [H])
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import evaluation as E  # same evaluation framework (head-anchored matching, top-N)

# tale file (normalized key) -> display name
NAMES = {
    "balikci": "Balıkçı", "ceviz": "Ceviz", "cirkinprens": "Çirkin Prens",
    "cizmelikedin": "Çizmeli Kedi", "esekokuz": "Eşek Öküz", "gumusayn": "Gümüş Ay",
    "guzelcirkin": "Güzel ve Çirkin", "habilkabil": "Habil Kabil",
    "hanselgretelv": "Hansel Gretel", "hansefendin": "Hans Efendi",
    "kagit": "Kağıt Prenses", "kamer": "Kamer", "kinalikuzu": "Kınalı Kuzu",
    "kirmizibasliklikiz2v": "Kırmızı Başlıklı Kız", "kurbagahenry": "Kurbağa Henry",
    "lustig": "Lustig", "pamukprenses2v": "Pamuk Prenses", "pinokyov": "Pinokyo",
    "polyannax": "Polyanna", "rapunzel": "Rapunzel", "sarmanx": "Sarman",
    "tasakusu": "Tasa Kuşu", "uyuyanguzel2": "Uyuyan Güzel",
    "vezirnureddin": "Vezir Nureddin", "zehrakisahikaye": "Zehra Kısa Hikaye",
}


def display_name(pred, gold):
    k = E.file_key(pred.get("story_file", ""))
    return NAMES.get(k) or gold.get("story") or k


# ===================== LaTeX formatting (your code, kept) =====================
def prf(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def vir(x, n=3):
    """Turkish decimal separator (dot -> comma)."""
    return f"{x:.{n}f}".replace(".", ",")


def latex_per_story(rows, kume, caption, label):
    sat = [
        r"\begin{table}[H]",
        r"\centering",
        r"\small",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\begin{tabular}{lccccccc}",
        r"\hline",
        (r"Hikâye Adı & Doğru Tespit & Yanlış/Fazla & Eksik/Kaçırılan "
         r"& Toplam & Precision & Recall & F1 Skoru \\"),
        r"\hline",
    ]
    TP = FP = FN = 0
    f1s = []
    for row in rows:
        d = row[kume]["dogru"]
        fz = row[kume]["fazla"]
        ek = row[kume]["eksik"]
        toplam = d + ek
        p, r, f = prf(d, fz, ek)
        TP += d
        FP += fz
        FN += ek
        f1s.append(f)
        sat.append(rf"{row['ad']} & {d} & {fz} & {ek} & {toplam} "
                   rf"& {vir(p)} & {vir(r)} & {vir(f)} \\")
    sat += [r"\hline", r"\end{tabular}", r"\end{table}"]
    mp, mr, mf = prf(TP, FP, FN)
    macro = sum(f1s) / len(f1s) if f1s else 0.0
    return "\n".join(sat), (mp, mr, mf, macro)


def latex_scores(scores, caption, label):
    mp, mr, mf, macro = scores
    sat = [
        r"\begin{table}[H]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\begin{tabular}{cccc}",
        r"\hline",
        r"Micro Precision & Micro Recall & Micro F1 Score & Macro F1 Score \\",
        r"\hline",
        rf"{vir(mp)} & {vir(mr)} & {vir(mf)} & {vir(macro)} \\",
        r"\hline",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(sat)


# ===================== Automatic number calculation (evaluation.py) =====================
def build_per_story(pred_path, ann_dir):
    gi = E.load_gold_index(ann_dir)
    with open(pred_path, encoding="utf-8") as fh:
        preds = json.load(fh)
    rows = []
    for p in preds:
        if "error" in p:
            continue
        g = gi.get(E.file_key(p.get("story_file", "")))
        if not g:
            print(f"UYARI: gold bulunamadı -> {p.get('story_file')}", file=sys.stderr)
            continue
        res = E.eval_story(p, g)
        a, t = res["char_main"], res["char_all"]
        rows.append({
            "ad": display_name(p, g),
            "ana": {"dogru": a["tp"], "fazla": a["fp"], "eksik": a["fn"]},
            "tum": {"dogru": t["tp"], "fazla": t["fp"], "eksik": t["fn"]},
        })
    rows.sort(key=lambda r: r["ad"].lower())
    return rows


def main():
    ap = argparse.ArgumentParser(description="Masal-bazlı karakter tespiti LaTeX tabloları (otomatik)")
    ap.add_argument("--predictions", default=os.path.join(SCRIPT_DIR, "predictions_after_t4.json"),
                    help="değerlendirilecek predictions JSON (varsayılan: current committed t4)")
    ap.add_argument("--annotations", default=os.path.join(SCRIPT_DIR, "test_data", "annotations"))
    ap.add_argument("--dump-json", default=None, help="hesaplanan PER_STORY'yi bu JSON'a da yaz")
    args = ap.parse_args()

    rows = build_per_story(args.predictions, args.annotations)
    if not rows:
        print("UYARI: hiç masal değerlendirilemedi (predictions/gold kontrol et).", file=sys.stderr)
        return
    if args.dump_json:
        with open(args.dump_json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)

    ana_tbl, ana_sc = latex_per_story(
        rows, "ana", "Ana Karakterler için Karakter Tespiti", "tab:ana-karakter")
    tum_tbl, tum_sc = latex_per_story(
        rows, "tum", "Tüm Karakterler için Karakter Tespiti", "tab:tum-karakter")

    print(ana_tbl, "\n")
    print(latex_scores(
        ana_sc, "Ana Karakterler için Karakter Tespiti Skorları", "tab:ana-skor"), "\n")
    print(tum_tbl, "\n")
    print(latex_scores(
        tum_sc, "Tüm Karakterler için Karakter Tespiti Skorları", "tab:tum-skor"))


if __name__ == "__main__":
    main()
