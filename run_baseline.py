# -*- coding: utf-8 -*-
"""
run_baseline.py — GUI'siz batch runner (FAZ 1).

Amaç: mainwindow.Ui_MainWindow.analiz_et'in ÇAĞRI SIRASINI birebir, GUI olmadan
tekrarlamak ve her masal için karakter + ilişki tahminlerini predictions.json'a
yazmak.

KISIT: analizClass / iliskiClass / mainwindow / main.py DEĞİŞTİRİLMEZ. Bu dosya
sadece onları import edip mevcut pipeline'ı sürer. Pipeline mantığı aynen kalır.

analiz_et akışı (mainwindow.py:587-604):
    analiz = MetinAnaliz(hikaye_yolu)
    sirali_gruplar = analiz.tum_islemler()        # -> karakterler.txt yazar (>=5)
    self.iliski.story_path = hikaye_yolu
    self.iliski.load_text()                        # karakterler.txt okur
    self.iliski.split_sentence_dialog()
    self.iliski.process()                          # -> self.iliski.all_relations

Dominant ilişki: overall_relation_graph (iliskiClass.py:228-237) içindeki
hesaplama BİREBİR replike edilir (sınıfa dokunmadan, all_relations okunarak).
"""

import argparse
import io
import json
import os
import sys
import traceback
from collections import Counter, defaultdict
from contextlib import redirect_stdout

# Windows konsolu cp1252 olabilir; Türkçe karakterler için stdout/stderr'i UTF-8'e al.
for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8")
    except Exception:
        pass

# Bu dosya proje/ içinde. CWD'yi buraya sabitle:
#  - import'lar (analizClass/iliskiClass) çözülsün
#  - MetinAnaliz.tum_islemler "karakterler.txt"i CWD'ye yazıyor (hardcoded relative)
#  - CharacterRelations.load_text "karakterler.txt"i CWD'den okuyor
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from analizClass import MetinAnaliz          # noqa: E402
from iliskiClass import CharacterRelations    # noqa: E402

HIKAYE_DIR = os.path.join(SCRIPT_DIR, "NLP-Hikayeler", "hikayeler")
KARAKTERLER_TXT = os.path.join(SCRIPT_DIR, "karakterler.txt")


def map_emotion(label):
    """savasy etiketlerini gold sözlüğüne (pozitif/negatif/notr) çevir.

    savasy/bert-base-turkish-sentiment-cased pratikte 'positive'/'negative'
    döndürür. Bilinmeyen etiket olduğu gibi bırakılır (görünür kalsın diye).
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
    return l  # bilinmeyen -> ham etiketi koru


def dominant_from_relations(all_relations):
    """iliskiClass.overall_relation_graph (satır 228-237) ile BİREBİR aynı:
    yönsüz sorted-pair + Counter.most_common ile çift başına tek baskın duygu."""
    relations_emotions = defaultdict(list)
    for relation in all_relations:
        c1, c2 = sorted([relation["from"], relation["to"]])
        relations_emotions[(c1, c2)].append(relation["emotion"])

    out = []
    raw_dominant = {}
    for pair, emotions in relations_emotions.items():
        counts = Counter(emotions)
        dominant_emotion = counts.most_common(1)[0][0]  # graf ile aynı tie-break
        raw_dominant[pair] = dominant_emotion
        out.append({"from": pair[0], "to": pair[1], "type": map_emotion(dominant_emotion)})
    return out, raw_dominant


def read_karakterler_txt(path=KARAKTERLER_TXT):
    """MetinAnaliz'in yazdığı karakterler.txt: 'kanonik,var1,var2,...' (>=5)."""
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
    """GUI'deki geri_git (mainwindow.py:563-576) ile aynı durum sıfırlaması.
    self.iliski GUI'de bir kez kurulur, masallar arasında resetlenir."""
    iliski.story_path = None
    iliski.variation_to_character = {}
    iliski.text = ""
    iliski.segments = []
    iliski.all_relations = []
    iliski.past_sentences = []
    iliski.is_dialog = False  # defansif (process zaten segment başına set ediyor)


def run_one(story_path, iliski, verbose_logs=False):
    """Tek masal için analiz_et akışını tekrarla, tahminleri sözlük olarak döndür."""
    story_file = os.path.basename(story_path)
    result = {"story_file": story_file}

    # ---- AŞAMA 1: Karakter tespiti (analiz_et: her masal için YENİ MetinAnaliz) ----
    analiz = MetinAnaliz(story_path)
    log1 = io.StringIO()
    with redirect_stdout(log1):
        sirali = analiz.tum_islemler()  # karakterler.txt yazar; [(isim,sayı),...] (>=5) döner

    raw_detected = sorted(analiz.characters)              # (a) TÜM tespit (filtre öncesi, ham)
    final_chars = [name for (name, cnt) in sirali]        # (b) ANA (>=5 eşiğini geçen, merged)
    final_counts = {name: cnt for (name, cnt) in sirali}
    spans = read_karakterler_txt()                        # >=5 kanonik -> varyasyonlar

    # ---- AŞAMA 2: İlişki çıkarımı (analiz_et: self.iliski yeniden kullanılır) ----
    reset_iliski(iliski)
    iliski.story_path = story_path
    log2 = io.StringIO()
    with redirect_stdout(log2):
        iliski.load_text()              # karakterler.txt (AŞAMA 1 çıktısı) okunur
        iliski.split_sentence_dialog()
        iliski.process()                # self.iliski.all_relations doldurulur

    relations, raw_dominant = dominant_from_relations(iliski.all_relations)
    raw_label_tally = Counter(r["emotion"] for r in iliski.all_relations)

    # ---- Şema (FAZ 1 onayı sonrası): ≥5 merged final liste = modelin KARAKTER tahmini.
    #      Hem "tüm" hem "ana" metriği bu tek liste üzerinden hesaplanır.
    #      Ham (filtre öncesi) liste SKORLANMAZ; yalnızca _diag'da referans kalır. ----
    result["characters"] = final_chars             # ≥5 merged final (geçiş sayısına göre AZALAN sıralı)
    result["character_counts"] = final_counts      # {kanonik: geçiş_sayısı} — ana = top-N seçimi için
    result["relations"] = relations                # [{from,to,type}], type ∈ {pozitif,negatif}

    # ---- Tanı/şeffaflık (SKORLANMAZ, sadece referans) ----
    result["_diag"] = {
        "raw_detected": raw_detected,              # (a) ham tespit (filtre öncesi) — SKORLANMAZ
        "n_raw_detected": len(raw_detected),
        "n_final_ge5": len(final_chars),
        "final_spans": spans,
        "threshold": 5,                            # kodda sabit (>=5); adaptif YOK
        "n_segments": len(iliski.segments),
        "n_all_relations": len(iliski.all_relations),
        "n_dominant_pairs": len(relations),
        "raw_emotion_labels": dict(raw_label_tally),
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
    print(f"[PRED] KARAKTER tahmini = ≥5 merged final — {d['n_final_ge5']} adet:")
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
        iliski = CharacterRelations(story_path=None)  # mainwindow.setupUi:9 ile aynı
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


if __name__ == "__main__":
    main()
