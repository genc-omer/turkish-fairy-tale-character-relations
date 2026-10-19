# Annotation Kuralları — Karakter ve İlişki Etiketleme

Bu belge, karakter ve ilişki etiketlemesinde uygulanan kuralları tanımlar. Kurallar, gold-standard manuel etiketlemenin tutarlılığını sağlamak amacıyla oluşturulmuştur.

## K1 — İlişki Seviyesi
İlişkiler cümle veya bölüm düzeyinde değil, tüm masal düzeyinde değerlendirilir ve her karakter çiftine tek bir baskın etiket atanır. Bu düzey, sistemin ürettiği genel ilişki grafiğiyle aynıdır.

## K2 — Dinamik İlişkiler
Masal boyunca değişen ilişkilerde son durum esas alınır. Bu kural yalnızca uzlaşma metinde fiilen canlandırılmışsa geçerlidir; doğrudan bir uzlaşma sahnesi yoksa, K10 uyarınca metinde canlandırılan baskın etkileşim etiketlenir (örn. Tüccar–Canavar: canlandırılan tek etkileşim tehdit olduğundan negatif).

## K3 — İlişki Tanımı
İki karakter arasında olay örgüsüne ilişkin anlamlı bir etkileşim bulunması, aralarında ilişki olduğunu gösterir; karşılıklı duygusal değer şart değildir. İlişkiler "sevgi/nefret" ekseninin yanı sıra "fayda/zarar" ekseninde de değerlendirilir. Örn. bir hayvanı çalan kişi ile hayvan arasındaki fail–mağdur ilişkisi negatiftir (Adam–Kınalı).

## K4 — Karakter Tanımı
Karakter SAYILIR:

- Özel adıyla geçen kişiler
- Tutarlı rolde ≥3 cümlede aktif adlandırılmış jenerikler (Anne, Cadı)
- Kişileştirilmiş varlıklar (konuşur, hisseder, plan yapar)

Karakter SAYILMAZ:

- Tek geçişli jenerikler (yoldan geçen yaşlı adam)
- Kolektif gruplar (kasaba halkı, arkadaşlar grubu — birey değil)
- Çerçeve hikaye anlatıcıları
- Geçmişte bahsedilen, olay örgüsünde aktif olmayan kişiler (ölmüş baba)

## K5 — Ana Karakter Kapsamı
Ana karakterler, olay örgüsünün merkezindeki protagonistler ile hikayenin temel gerilimini taşıyan kişilerdir. Merkez ilişkinin diğer ucu (örn. Gepetto) ve süregelen tek baskın antagonist (örn. Kötü Kalpli Kraliçe) bu kapsama girer. Sürekli sahnede bulunsa dahi yardımcı karakterler ile sıralı/geçici antagonistler ana karakter sayılmaz.

## K6 — Nötr ve Pozitif Ayrımı
Duygusal yük taşımayan simetrik değişimler (örn. para–mal ticareti) nötr kabul edilir. Asimetrik fayda veya minnet aktarımı ise K3 uyarınca pozitiftir. Örn. eşek alışverişi (Çiftçi–Yaşlı Amca) nötr; minnetle verilen ve faydalanılan hediye (Lustig–Kadın) pozitiftir.

## K7 — Kapsam
Yalnızca protagonist merkezli ilişkiler değil, metindeki tüm anlamlı karakter çiftleri etiketlenir (örn. Zehra'da Begüm–Cansu–Aylin arasındaki olumlu ilişki).

## K8 — İsimlendirme
Her karakter için metinde en sık veya en tam geçen biçim kanonik isim olarak alınır. Varyasyonlar ayrı bir alanda (char_spans) tutulur; ana isim tek kalır.

## K9 — İlişki Yönü
İlişkiler yönsüz olarak ele alınır ve her çifte tek etiket atanır (sistem yönsüz graf kullanır). Belirgin asimetri durumunda istisnaen iki kayıt ve açıklama eklenir.

## K10 — Canlandırılma Şartı
Yalnızca metinde fiilen etkileşen veya birlikte geçen çiftler etiketlenir; ima edilen ancak sahne ya da cümle paylaşmayan ilişkiler etiketlenmez. Gerekçe: Sistem ilişkiyi metinden çıkardığından, canlandırılmamış ilişkiler tespit edilemez; bu ilişkilerin dışlanması ile değerlendirmenin adilliği korunmuş olur.

## K11 — Aldatma ve Zarar
Aldatma veya manipülasyonun negatif sayılması için aldatılan tarafın zarar görmesi gerekir. Zarar doğurmayan aldatmalarda yüzey duygu esas alınır (genellikle pozitif). Örn. Çizmeli Kedi'de kral zarar görmediğinden ilişki pozitif; Delikanlı'nın Hans'ı sömürmesi negatiftir.
