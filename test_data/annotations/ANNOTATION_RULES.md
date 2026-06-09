# Annotation Kuralları — Karakter ve İlişki Etiketleme

Bu belge, gold-standard manuel etiketlemenin tutarlılığını sağlamak için 
oluşturulmuştur. İki bağımsız etiketleme (Claude + Gemini) çapraz kontrol 
edilerek üzerinde uzlaşılan kurallardır.

## K1 — İlişki Seviyesi
Tüm masal seviyesinde, karakter çifti başına TEK dominant ilişki. 
Bölüm/cümle seviyesi kullanılmaz. (Mevcut modelin overall_relation_graph 
çıktısıyla aynı seviye.)

## K2 — Netleştirme (canlandırma şartı ile etkileşimi)
Son durum kuralı (K2) ancak çiftin uzlaşması/değişimi metinde FİİLEN 
canlandırılmışsa uygulanır (örn. "Salih onu affetti" — doğrudan). 
Mutlu sonda taraflar sadece aynı mekânda birlikte bulunuyor ama 
aralarında doğrudan uzlaşma sahnesi yoksa, K10 gereği canlandırılan 
baskın etkileşim etiketlenir (örn. Tüccar-Canavar: tek canlandırılan 
etkileşim tehdit → negatif).


## K3 — İlişki Tanımı (Tanım B: Etkileşim Temelli)
İki karakter arasında anlamlı olay örgüsü etkileşimi varsa ilişki vardır. 
Karşılıklı duygusal değer şart değildir. İlişkiler "sevgi/nefret" kadar 
"fayda sağlama / zarar verme" ekseninde de değerlendirilir.
- Örn: Hırsız bir hayvanı çalarsa, hayvana kişisel nefreti olmasa da 
  fail-mağdur ilişkisi NEGATİF'tir. (Adam-Kınalı)

## K4 — Karakter Tanımı
Karakter SAYILIR:
- Özel ad geçen kişiler
- Tutarlı rolde ≥3 cümlede aktif adlandırılmış jenerikler (Anne, Cadı)
- Kişileştirilmiş varlık (konuşur, hisseder, plan yapar)

Karakter SAYILMAZ:
- Tek-geçişli jenerikler (yoldan geçen yaşlı adam)
- Kolektif gruplar (kasaba halkı, arkadaşlar grubu — birey değil)
- Çerçeve hikaye anlatıcıları (ayrı tutulur veya hariç)
- Geçmişte bahsedilen, olay örgüsünde aktif olmayan kişiler (ölmüş baba)

## K5 — Ek netleştirme: ana karakter kapsamı
Ana karakter = olay örgüsünün merkezindekiler: protagonist(ler) + 
hikayenin temel gerilimini/duygusal eksenini taşıyanlar:
- Deuteragonist / baba-evlat gibi merkez ilişkinin diğer ucu (Gepetto)
- Hikaye boyunca SÜREGELEN tek baskın antagonist (Kötü Kalpli Kraliçe)
Ana DEĞİL:
- Yardımcı/akıl veren/sidekick — sürekli sahnede olsa bile (Çekirge, 
  Mavi Peri, Ceviz'de Anne)
- Sıralı/geçici engel-antagonistler (art arda gelen ayrı kötüler: 
  Hansel-Gretel'de Üvey Anne+Cadı, Zehra'da zorba grubu)
  
## K6 — Ek netleştirme: notr vs fayda
Simetrik, duygusal yük taşımayan değişim (para↔mal ticareti) = notr. 
Ama asimetrik fayda/minnet aktarımı (örn. minnetle verilen hediye, 
tek tarafın doğrudan yararlandığı durum) = K3 gereği pozitif.
- Örn: Çiftçi-Yaşlı Amca (eşek alışverişi) → notr.
- Karşıt: Lustig-Kadın (minnet hediyesi kuzu, Lustig faydalanır) → pozitif.

## K7 — Kapsam
Tüm anlamlı karakter çiftleri etiketlenir — sadece protagonist-merkezli 
değil. Örn: Zehra hikayesinde Begüm-Cansu-Aylin'in kendi aralarındaki 
pozitif arkadaşlık da etiketlenir.

## K8 — İsimlendirme
Her karakter için TEK kanonik isim (metinde en sık/en tam geçen form). 
Örn: "Ali Çoban", "Cahide Hanım". Varyasyonlar gerekiyorsa ayrı bir 
char_spans alanında tutulur, ana isim tek kalır.

## K9 — İlişki Yönü
Undirected (yönsüz). Çift başına tek etiket. Mevcut sistem yönsüz graf 
kullandığı için (sorted pair). Gerçekten asimetrik bir ilişki varsa 
istisna olarak iki kayıt + not.

## K10 — Metinde Canlandırılma Şartı
Sadece metinde fiilen etkileşen / birlikte geçen karakter çiftleri 
etiketlenir. İma edilen ama sahne/cümle paylaşmayan ilişkiler (örn. aynı 
evde yaşayan ama doğrudan etkileşmeyen anne-çocuk) etiketlenmez. 
Gerekçe: Model ilişkiyi metinden çıkarır; canlandırılmamış ilişki 
modelce tespit edilemez, değerlendirme adil kalır.

## K11 — Ek netleştirme: aldatma + zarar
Aldatma/manipülasyon NEGATİF olması için aldatılan tarafın ZARAR/sömürü 
görmesi gerekir. Kurbanı zarar görmeyen "iyiniyetli aldatma" yüzey 
duyguyu izler (genelde pozitif).
- Örn: Çizmeli Kedi kralı kandırır ama kral memnun + damat kazanır 
  (zarar yok) → pozitif.
- Karşıt: Delikanlı Hans'ı yalanla sömürür (zarar) → negatif.