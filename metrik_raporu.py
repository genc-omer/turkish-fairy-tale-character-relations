#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
METRIC REPORT — VISUAL (HTML + Markdown)
Prints the numbers of karakter_tablolari.py + iliski_tablolari.py in a READABLE/VISUAL
form instead of LaTeX: styled HTML (in the browser, F1 color-coded) and GitHub Markdown tables.
All of Tables 5.1–5.9 + a current-vs-last-year headline card at the top.

USAGE:
    python metrik_raporu.py                       # current = predictions_after_t4.json
    python metrik_raporu.py --predictions predictions_after_odak1.json
    python metrik_raporu.py --out-dir .           # output folder
Output: metrik_raporu.html + metrik_raporu.md
"""
import argparse, os, sys, html
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import evaluation as E
import karakter_tablolari as K
import iliski_tablolari as I
from karakter_tablolari import prf, vir

GECEN_YIL = {"ana": 0.908, "tum": 0.818, "poz": 0.671, "neg": 0.489}  # approximate reference

def edge_rows(rows, kume):
    """[ad,d,fz,ek,toplam,P,R,F1] rows + (microP,microR,microF1,macroF1)."""
    out=[]; TP=FP=FN=0; f1s=[]
    for r in rows:
        d,fz,ek = r[kume]["dogru"], r[kume]["fazla"], r[kume]["eksik"]
        p,rc,f = prf(d,fz,ek); TP+=d; FP+=fz; FN+=ek; f1s.append(f)
        out.append([r["ad"],d,fz,ek,d+ek,p,rc,f])
    mp,mr,mf = prf(TP,FP,FN); macro = sum(f1s)/len(f1s) if f1s else 0
    return out, (mp,mr,mf,macro)

# ---------------- HTML ----------------
def f1bg(f):
    return f"background: rgba(46,160,67,{f*0.80:.2f});" + ("color:#fff;" if f>=0.7 else "")

def h_tbl(caption, headers, rows, f1col=None):
    s=[f'<table><caption>{html.escape(caption)}</caption><thead><tr>']
    s += [f'<th>{html.escape(str(h))}</th>' for h in headers]
    s.append('</tr></thead><tbody>')
    for row in rows:
        s.append('<tr>')
        for j,c in enumerate(row):
            style = f1bg(c) if (f1col is not None and j==f1col and isinstance(c,float)) else ""
            val = vir(c) if isinstance(c,float) else html.escape(str(c))
            cls = ' class="num"' if (isinstance(c,(int,float)) or j>0) else ''
            s.append(f'<td{cls} style="{style}">{val}</td>')
        s.append('</tr>')
    s.append('</tbody></table>')
    return "".join(s)

def h_scores(sc):
    mp,mr,mf,ma=sc
    return ('<table class="scores"><thead><tr><th>Micro P</th><th>Micro R</th>'
            '<th>Micro F1</th><th>Macro F1</th></tr></thead><tbody><tr>'
            f'<td class="num">{vir(mp)}</td><td class="num">{vir(mr)}</td>'
            f'<td class="num">{vir(mf)}</td><td class="num"><b>{vir(ma)}</b></td>'
            '</tr></tbody></table>')

def headline(kchar, irows):
    _,ana_sc = edge_rows(kchar,"ana"); _,tum_sc = edge_rows(kchar,"tum")
    pd=sum(r["poz"]["dogru"] for r in irows); pt=sum(r["poz"]["toplam"] for r in irows)
    nd=sum(r["neg"]["dogru"] for r in irows); nt=sum(r["neg"]["toplam"] for r in irows)
    cur={"ana":ana_sc[3],"tum":tum_sc[3],"poz":pd/pt if pt else 0,"neg":nd/nt if nt else 0}
    labels={"ana":"Ana karakter F1","tum":"Tüm karakter F1","poz":"Pozitif ilişki","neg":"Negatif ilişki"}
    cards=[]
    for k in ("ana","tum","poz","neg"):
        c=cur[k]*100; g=GECEN_YIL[k]*100
        cards.append(f'<div class="card"><div class="lbl">{labels[k]}</div>'
                     f'<div class="big">{c:.1f}<span class="pct">%</span></div>'
                     f'<div class="ref">geçen yıl ≈ {g:.1f} (yaklaşık)</div></div>')
    return '<div class="cards">'+"".join(cards)+'</div>'

CSS = """
body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:#1a1a1a;background:#fafbfc}
h1{font-size:1.5rem} h2{margin-top:34px;border-bottom:2px solid #2980b9;padding-bottom:6px;color:#1a5276}
table{border-collapse:collapse;width:100%;margin:10px 0 26px;font-size:.86rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}
caption{caption-side:top;text-align:left;font-weight:600;margin-bottom:6px;color:#333}
th{background:#2980b9;color:#fff;padding:7px 9px;text-align:left;font-weight:600}
td{padding:6px 9px;border-bottom:1px solid #e5e8ec}
td.num{text-align:center;font-variant-numeric:tabular-nums}
tbody tr:nth-child(even){background:#f4f7fa}
table.scores{width:auto} table.scores td,table.scores th{text-align:center;padding:6px 18px}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0}
.card{flex:1;min-width:180px;background:#fff;border:1px solid #e0e4e8;border-radius:10px;padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.card .lbl{font-size:.8rem;color:#667} .card .big{font-size:2rem;font-weight:700;color:#1a5276}
.card .pct{font-size:1rem;color:#88a} .card .ref{font-size:.72rem;color:#99a;margin-top:2px}
.note{background:#fff7e6;border-left:4px solid #f0a000;padding:10px 14px;border-radius:6px;font-size:.82rem;margin:14px 0}
"""

def build_html(kchar, irows, cfg):
    H=[f'<!doctype html><html lang="tr"><head><meta charset="utf-8">',
       f'<title>Metrik Raporu — {html.escape(cfg)}</title><style>{CSS}</style></head><body>']
    H.append(f'<h1>Karakter &amp; İlişki Metrik Raporu</h1>')
    H.append(f'<p style="color:#667">Yapılandırma: <b>{html.escape(cfg)}</b> · '
             'tüm sayılar dondurulmuş gold + head-anchored değerlendirme ile.</p>')
    H.append(headline(kchar, irows))
    H.append('<div class="note">⚠️ Geçen yıl referansı <b>yaklaşıktır</b> — farklı/sıkı gold + '
             'top-N ana proxy + katı eşleştirme nedeniyle birebir kıyaslanamaz. Pozitif/negatif '
             'oranlarında ~±1-2 çift GPU gürültü tabanı vardır (edge-bulma deterministik).</div>')
    # Character
    H.append('<h2>Karakter Tespiti (Tablo 5.1–5.4)</h2>')
    ch=["Hikâye","Doğru","Yanlış/Fazla","Eksik","Toplam","Precision","Recall","F1"]
    ar,asc=edge_rows(kchar,"ana"); tr,tsc=edge_rows(kchar,"tum")
    H.append(h_tbl("Tablo 5.1 — Ana Karakterler için Karakter Tespiti", ch, ar, f1col=7))
    H.append('<p><b>Skorlar (Ana):</b></p>'+h_scores(asc))
    H.append(h_tbl("Tablo 5.3 — Tüm Karakterler için Karakter Tespiti", ch, tr, f1col=7))
    H.append('<p><b>Skorlar (Tüm):</b></p>'+h_scores(tsc))
    # Relation
    H.append('<h2>Karakterler Arası İlişki Tespiti (Tablo 5.5–5.9)</h2>')
    ih=["Hikâye","Doğru","Yanlış/Fazla","Eksik","Toplam","Precision","Recall","F1"]
    iar,iasc=edge_rows(irows,"ana"); itr,itsc=edge_rows(irows,"tum")
    H.append(h_tbl("Tablo 5.5 — Ana Karakterler Arası İlişki Tespiti", ih, iar, f1col=7))
    H.append('<p><b>Skorlar (Ana ilişki):</b></p>'+h_scores(iasc))
    H.append(h_tbl("Tablo 5.7 — Tüm Karakterler Arası İlişki Tespiti", ih, itr, f1col=7))
    H.append('<p><b>Skorlar (Tüm ilişki):</b></p>'+h_scores(itsc))
    # poz/neg
    pn=[]; pd=pt=nd=nt=0
    for r in irows:
        p,pt_,n,nt_=r["poz"]["dogru"],r["poz"]["toplam"],r["neg"]["dogru"],r["neg"]["toplam"]
        pd+=p;pt+=pt_;nd+=n;nt+=nt_
        pn.append([r["ad"],f"{p} / {pt_}",f"{n} / {nt_}",f"{p+n} / {pt_+nt_}"])
    pn.append(["<b>Toplam</b>",f"<b>{pd} / {pt}</b>",f"<b>{nd} / {nt}</b>",f"<b>{pd+nd} / {pt+nt}</b>"])
    pn.append(["<b>Başarı Oranı</b>",f"<b>{vir(pd/pt if pt else 0)}</b>",
               f"<b>{vir(nd/nt if nt else 0)}</b>",f"<b>{vir((pd+nd)/(pt+nt) if pt+nt else 0)}</b>"])
    # the poz/neg table already contains HTML -> render with escaping off
    s=['<table><caption>Tablo 5.9 — Doğru Bulunan Pozitif ve Negatif İlişki Oranları</caption>',
       '<thead><tr><th>Hikâye</th><th>Pozitif (doğru/toplam)</th><th>Negatif (doğru/toplam)</th><th>Toplam</th></tr></thead><tbody>']
    for row in pn:
        s.append('<tr>'+''.join(f'<td class="num">{c}</td>' if j>0 else f'<td>{c}</td>' for j,c in enumerate(row))+'</tr>')
    s.append('</tbody></table>')
    H.append("".join(s))
    H.append('</body></html>')
    return "\n".join(H)

# ---------------- Markdown ----------------
def md_tbl(caption, headers, rows):
    L=[f"**{caption}**","","| "+" | ".join(headers)+" |","|"+"|".join(["---"]*len(headers))+"|"]
    for row in rows:
        L.append("| "+" | ".join(vir(c) if isinstance(c,float) else str(c) for c in row)+" |")
    return "\n".join(L)+"\n"

def build_md(kchar, irows, cfg):
    M=[f"# Karakter & İlişki Metrik Raporu",f"_Yapılandırma: **{cfg}**_",""]
    ch=["Hikâye","Doğru","Yanlış/Fazla","Eksik","Toplam","Precision","Recall","F1"]
    for kume,cap in [("ana","Tablo 5.1 — Ana Karakter Tespiti"),("tum","Tablo 5.3 — Tüm Karakter Tespiti")]:
        rws,sc=edge_rows(kchar,kume); M.append(md_tbl(cap,ch,rws))
        M.append(f"*Skorlar:* micro P/R/F1 = {vir(sc[0])}/{vir(sc[1])}/{vir(sc[2])}, **macro F1 = {vir(sc[3])}**\n")
    for kume,cap in [("ana","Tablo 5.5 — Ana Karakterler Arası İlişki"),("tum","Tablo 5.7 — Tüm Karakterler Arası İlişki")]:
        rws,sc=edge_rows(irows,kume); M.append(md_tbl(cap,ch,rws))
        M.append(f"*Skorlar:* micro P/R/F1 = {vir(sc[0])}/{vir(sc[1])}/{vir(sc[2])}, **macro F1 = {vir(sc[3])}**\n")
    pn=[]; pd=pt=nd=nt=0
    for r in irows:
        p,pt_,n,nt_=r["poz"]["dogru"],r["poz"]["toplam"],r["neg"]["dogru"],r["neg"]["toplam"]
        pd+=p;pt+=pt_;nd+=n;nt+=nt_; pn.append([r["ad"],f"{p} / {pt_}",f"{n} / {nt_}",f"{p+n} / {pt_+nt_}"])
    pn.append(["Toplam",f"{pd} / {pt}",f"{nd} / {nt}",f"{pd+nd} / {pt+nt}"])
    pn.append(["Başarı Oranı",vir(pd/pt if pt else 0),vir(nd/nt if nt else 0),vir((pd+nd)/(pt+nt) if pt+nt else 0)])
    M.append(md_tbl("Tablo 5.9 — Pozitif/Negatif İlişki Oranları",
                    ["Hikâye","Pozitif d/t","Negatif d/t","Toplam d/t"], pn))
    return "\n".join(M)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--predictions", default=os.path.join(SCRIPT_DIR,"predictions_after_t4.json"))
    ap.add_argument("--annotations", default=os.path.join(SCRIPT_DIR,"test_data","annotations"))
    ap.add_argument("--out-dir", default="/mnt/user-data/outputs")
    args=ap.parse_args()
    kchar=K.build_per_story(args.predictions,args.annotations)
    irows=I.build_rows(args.predictions,args.annotations)
    if not kchar: print("UYARI: veri yok",file=sys.stderr); return
    cfg=os.path.basename(args.predictions)
    os.makedirs(args.out_dir,exist_ok=True)
    hp=os.path.join(args.out_dir,"metrik_raporu.html"); mp=os.path.join(args.out_dir,"metrik_raporu.md")
    open(hp,"w",encoding="utf-8").write(build_html(kchar,irows,cfg))
    open(mp,"w",encoding="utf-8").write(build_md(kchar,irows,cfg))
    print("YAZILDI:",hp); print("YAZILDI:",mp)

if __name__=="__main__":
    main()
