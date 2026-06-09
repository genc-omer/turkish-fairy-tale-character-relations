#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARAKTERLER ARASI İLİŞKİ — MASAL-BAZLI LaTeX TABLO ÜRETİCİ (OTOMATİK)
Eski rapordaki Tablo 5.5–5.9 biçiminde üretir:
  5.5 Ana Karakterler için Karakterler Arası İlişki Tespiti     (per-story)
  5.6 Ana ... Skorları                                          (micro/macro)
  5.7 Tüm Karakterler için Karakterler Arası İlişki Tespiti     (per-story)
  5.8 Tüm ... Skorları
  5.9 Her Hikaye İçin Doğru Bulunan Pozitif/Negatif İlişki Oranları

Sayılar evaluation.py + gold'dan OTOMATİK hesaplanır (manuel doldurma yok).
Metodoloji evaluation.py ile birebir:
  - İlişki (edge) = yönsüz çift; valanstan BAĞIMSIZ (çift bulunduysa doğru/TP).
  - tüm  : tüm gold çiftleri (eval_story.edge).
  - ana  : iki ucu da gold ANA karaktere düşen çiftler.
  - poz/neg oranı = doğru valansla bulunan / toplam gold (sınıf C), notr_handling='exclude'.

GÜRÜLTÜ NOTU: edge-bulma DETERMİNİSTİK değil ama 5-koşuda TP sabit (gürültüsüz);
poz/neg valansında ~±1-2 çift GPU gürültüsü vardır → Tablo 5.9 tek-snapshot, tezde
çok-koşu ort±σ ile verilmesi önerilir.

KULLANIM:
    python iliski_tablolari.py                       # current = predictions_after_t4.json
    python iliski_tablolari.py > iliski_tablolar.tex
    python iliski_tablolari.py --predictions predictions_after_odak1.json
LaTeX'te gereken: \\usepackage{float}
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import evaluation as E
from karakter_tablolari import NAMES, display_name, prf, vir  # ortak yardımcılar


def ana_edge_counts(pred, gold):
    """İki ucu da gold ANA karaktere düşen ilişki çiftleri için TP/FP/FN."""
    spans = gold.get("char_spans", {})
    gc = gold["characters"]
    mains = set(E.norm(c) for c in gold.get("main_characters", []))
    p2g = E.match_characters(pred.get("characters", []), gc, spans)
    nmap = {pred["characters"][i]: gc[g] for i, (g, _t) in p2g.items()}
    gold_ana = set()
    for r in gold.get("relations", []):
        if E.norm(r["from"]) in mains and E.norm(r["to"]) in mains:
            gold_ana.add(E.pair_key(r["from"], r["to"]))
    pred_ana = set()
    for r in pred.get("relations", []):
        a = nmap.get(r["from"]); b = nmap.get(r["to"])
        if a and b and E.norm(a) != E.norm(b) and E.norm(a) in mains and E.norm(b) in mains:
            pred_ana.add(E.pair_key(a, b))
    return len(gold_ana & pred_ana), len(pred_ana - gold_ana), len(gold_ana - pred_ana)


def build_rows(pred_path, ann_dir):
    gi = E.load_gold_index(ann_dir)
    with open(pred_path, encoding="utf-8") as fh:
        preds = json.load(fh)
    rows = []
    for p in preds:
        if "error" in p:
            continue
        g = gi.get(E.file_key(p.get("story_file", "")))
        if not g:
            print(f"UYARI: gold bulunamadı -> {p.get('story_file')}", file=sys.stderr); continue
        res = E.eval_story(p, g)
        atp, afp, afn = ana_edge_counts(p, g)
        t = res["edge"]
        ptp, pfp, pfn, _ = E.class_counts(res["valence_universe"], "pozitif", "exclude")
        ntp, nfp, nfn, _ = E.class_counts(res["valence_universe"], "negatif", "exclude")
        rows.append({
            "ad": display_name(p, g),
            "ana": {"dogru": atp, "fazla": afp, "eksik": afn},
            "tum": {"dogru": t["tp"], "fazla": t["fp"], "eksik": t["fn"]},
            "poz": {"dogru": ptp, "toplam": ptp + pfn},
            "neg": {"dogru": ntp, "toplam": ntp + nfn},
        })
    rows.sort(key=lambda r: r["ad"].lower())
    return rows


def latex_edge(rows, kume, caption, label):
    sat = [
        r"\begin{table}[H]", r"\centering", r"\small",
        rf"\caption{{{caption}}}", rf"\label{{{label}}}",
        r"\begin{tabular}{lccccccc}", r"\hline",
        (r"Hikâye Adı & Doğru Tespit & Yanlış/Fazla & Eksik/Kaçırılan "
         r"& Toplam & Precision & Recall & F1 Skoru \\"),
        r"\hline",
    ]
    TP = FP = FN = 0; f1s = []
    for row in rows:
        d, fz, ek = row[kume]["dogru"], row[kume]["fazla"], row[kume]["eksik"]
        toplam = d + ek
        p, r, f = prf(d, fz, ek)
        TP += d; FP += fz; FN += ek; f1s.append(f)
        sat.append(rf"{row['ad']} & {d} & {fz} & {ek} & {toplam} & {vir(p)} & {vir(r)} & {vir(f)} \\")
    sat += [r"\hline", r"\end{tabular}", r"\end{table}"]
    mp, mr, mf = prf(TP, FP, FN)
    macro = sum(f1s) / len(f1s) if f1s else 0.0
    return "\n".join(sat), (mp, mr, mf, macro)


def latex_scores(scores, caption, label):
    mp, mr, mf, macro = scores
    return "\n".join([
        r"\begin{table}[H]", r"\centering",
        rf"\caption{{{caption}}}", rf"\label{{{label}}}",
        r"\begin{tabular}{cccc}", r"\hline",
        r"Micro Precision & Micro Recall & Micro F1 Score & Macro F1 Score \\", r"\hline",
        rf"{vir(mp)} & {vir(mr)} & {vir(mf)} & {vir(macro)} \\",
        r"\hline", r"\end{tabular}", r"\end{table}",
    ])


def latex_posneg(rows, caption, label):
    sat = [
        r"\begin{table}[H]", r"\centering", r"\small",
        rf"\caption{{{caption}}}", rf"\label{{{label}}}",
        r"\begin{tabular}{lccc}", r"\hline",
        (r"Hikâye Adı & Doğru Bulunan Pozitif & Doğru Bulunan Negatif "
         r"& Toplam Doğru Bulunan \\"),
        r"\hline",
    ]
    pd = pt = nd = nt = 0
    for row in rows:
        pdg, ptg = row["poz"]["dogru"], row["poz"]["toplam"]
        ndg, ntg = row["neg"]["dogru"], row["neg"]["toplam"]
        pd += pdg; pt += ptg; nd += ndg; nt += ntg
        sat.append(rf"{row['ad']} & {pdg} / {ptg} & {ndg} / {ntg} & {pdg+ndg} / {ptg+ntg} \\")
    sat += [r"\hline",
            rf"Toplam & {pd} / {pt} & {nd} / {nt} & {pd+nd} / {pt+nt} \\",
            rf"Toplam Başarı Oranı & {vir(pd/pt if pt else 0)} & {vir(nd/nt if nt else 0)} "
            rf"& {vir((pd+nd)/(pt+nt) if (pt+nt) else 0)} \\",
            r"\hline", r"\end{tabular}", r"\end{table}"]
    return "\n".join(sat)


def main():
    ap = argparse.ArgumentParser(description="Masal-bazlı karakterler arası ilişki LaTeX tabloları (otomatik)")
    ap.add_argument("--predictions", default=os.path.join(SCRIPT_DIR, "predictions_after_t4.json"))
    ap.add_argument("--annotations", default=os.path.join(SCRIPT_DIR, "test_data", "annotations"))
    ap.add_argument("--dump-json", default=None)
    args = ap.parse_args()

    rows = build_rows(args.predictions, args.annotations)
    if not rows:
        print("UYARI: hiç masal değerlendirilemedi.", file=sys.stderr); return
    if args.dump_json:
        with open(args.dump_json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)

    ana_tbl, ana_sc = latex_edge(rows, "ana",
        "Ana Karakterler için Karakterler Arası İlişki Tespiti", "tab:ana-iliski")
    tum_tbl, tum_sc = latex_edge(rows, "tum",
        "Tüm Karakterler için Karakterler Arası İlişki Tespiti", "tab:tum-iliski")

    print(ana_tbl, "\n")
    print(latex_scores(ana_sc, "Ana Karakterler için Karakterler Arası İlişki Tespiti Skorları", "tab:ana-iliski-skor"), "\n")
    print(tum_tbl, "\n")
    print(latex_scores(tum_sc, "Tüm Karakterler için Karakterler Arası İlişki Tespiti Skorları", "tab:tum-iliski-skor"), "\n")
    print(latex_posneg(rows,
        "Her Hikaye İçin Doğru Bulunan Pozitif ve Negatif Karakter İlişkileri", "tab:posneg"))


if __name__ == "__main__":
    main()
