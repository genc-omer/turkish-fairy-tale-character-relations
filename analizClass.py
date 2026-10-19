from collections import Counter, defaultdict
from difflib import get_close_matches
import re
import string
import spacy
from spacy import displacy
from nltk.tokenize import word_tokenize

class MetinAnaliz:
    def __init__(self,path_hikaye, model_name="tr_core_news_trf"):
        self.path=path_hikaye
        self.nlp = spacy.load(model_name)
        self.insansi_eylemler = {
            "duy", "sor", "sus", "git", "oyna", "hazırla", "paylaş", "tut", "ör", "söyle", "de", "konuş", 
            "düşün", "hisset", "hissed", "koyul", "kazan", "dokun", "tat", "yürü", "koş", "uyu", "uyan", 
            "gülümse", "ağla", "gül", "sev", "kork", "özlem", "iste", "hatırla", "unut", "kız", "öfkelen", 
            "öfke", "eğit", "uyar", "heyecanlan", "hüzünlen", "endişelen", "sevin", "üzül", "merak", "meraklan", 
            "kıskan", "ilgil", "sabırsızlan", "sakinleş", "kandır", "inandır", "cesaretlendir", "et", "incele", 
            "anla", "farket", "duygulan", "güven", "şüphelen", "şüphe", "destekle", "yargıla", "suçla", 
            "affet", "umutla", "eğlen", "rahatla", "çabala", "düşle", "şaşır", "şaş", "şevklen", "iste", 
            "koru", "gül", "ver", "yap", "bak", "öğren", "özle", "dinle", "planla", "arzula", "hedefle", "sor",
            "gözlemle", "çöz", "kararlaştır", "reddet", "dinlen", "korkut", "izle", "oku", "anlat", "çalış", "katıl",
            "yaz", "tartış", "hissizleş", "yüreklen", "yüreklendir", "gizle", "dile", "anlamlandır", "öv", 
            "döv", "eleştir", "sorgula", "haket", "diren", "vazgeç", "anlaş", "bağışla", "bağır", "mırıldan", "ye", 
            "çalış", "konuş", "al", "dile", "kız", "kır", "kırıl", "hastalan"
        }
        self.turkce_stopwords = {
        "bir", "bu", "şu", "çok", "daha", "mi", "mu", "mı", "mü", "şey", "tane",
        "ve","ile", "de", "da", "ki", "ne", "ni", "için", "ama", "fakat", "ancak",
        "gibi", "ise", "en", "ya", "iç", "herkes","kimse","kendi","\"","“"," ","",
        "hem", "veya", "ya da", "çünkü", "lakin", "diye", "kadar", "sonra", "kişi",
        "önce", "her", "hiç", "hep", "bazı", "tüm", "hangi", "neden", "nasıl", "nerede", "ne zaman",
        "a", "na", "dan", "den", "e", "ye", "deki", "daki", "deki", "deki", "deki", "deki",
        "nin", "nin", "nın", "nun", "nün", "ki", "mı", "mi", "mu", "mü","içi","ses",
        "ya", "ya da", "ya da", "ya da", "ya da", "ya da", "ya da", "ya da","ben", "sen", "o","ora","bura","şura","orada","burada","şurada","biri","biz","siz"
        }
        # Odak 4: BARE (single-word, no compound) non-personified environmental/abstract/collective
        # entities; removed only in the dependency (nsubj + human verb) branch.
        # NOTE: güneş/ay/yıldız (sun/moon/star) are left out ON PURPOSE; in a tale a personified
        #      celestial body can be a character (in the Kamer gold, Güneş and Yıldız are real characters).
        self.non_karakter = {
            # environmental / natural phenomena / abstract
            "fırtına", "rüzgar", "rüzgâr", "yağmur", "kar", "dolu", "sis", "bulut",
            "gök", "gökyüzü", "zaman", "gece", "gündüz", "sabah", "akşam", "mevsim",
            "ses", "ışık", "gölge", "rüya", "kader", "ölüm",
            # collective groups (not individuals)
            "insanlar", "herkes", "kasabalılar", "köylüler", "halk", "bayanlar",
            "beyler", "saraydakiler", "askerler", "çocuklar", "kuşlar", "hayvanlar",
        }
        self.characters = set()
        self.character_counter = Counter()
        self.sentences_by_character = defaultdict(list)
        self.groups = []


    def text_preprocess(self,text):
        text = text.replace("’", "'")  # convert ’ to '
        text = text.replace("“", '"')  #  convert “ to "
        text = text.replace("”", '"')  #  convert ” to "
        text = re.sub(r"'(\s+)", "'", text)  # drop spaces after an apostrophe
        return text

    def clean_word(self, word):
        return re.split(r"'", word)[0].lower()
    
    
    def get_modifier_chain(self,token):
        modifiers = []
        stack = [token]

        while stack:
            current = stack.pop()
            if current not in modifiers:
                modifiers.append(current)
            for child in current.children:
                if child.dep_ in ["amod", "compound", "nmod:poss", "nmod", "flat"]:
                    stack.append(child)

        if len(modifiers) >= 1:
            modifiers = sorted(modifiers, key=lambda x: x.i)
            return " ".join([t.text.lower() for t in modifiers])
        else:
            return None
        
    def is_sublist_or_subset(self, small, big):
        for i in range(len(big) - len(small) + 1):
            if big[i:i+len(small)] == small:
                return True
        return set(small).issubset(set(big))

    def get_head_word(self, phrase):
        doc = self.nlp(phrase)
        if len(doc) == 0:
            return None
        return doc[-1].lemma_.lower()

    def _iyelik_sahibi_mi(self, single_word, phrase, head_word):
        """Over-merge fix (P1, possessive absorption).
        In an 'X'in Y' possessive phrase, a single-word possessor (X) that is NOT
        the head word (Y) is a separate entity. E.g. 'hansel' ∈ 'hansel gretel'in
        babası', but hansel is the POSSESSOR and baba is the HEAD, so hansel is not
        absorbed into the father's group. Apposition ('ali çoban' ⊇ 'ali') has NO
        genitive marker, so this returns False and the old behavior is kept."""
        toks = phrase.split()
        gen = re.compile(r"'(in|ın|un|ün|nin|nın|nun|nün)$", re.IGNORECASE)
        if not any(gen.search(t) for t in toks):
            return False
        if single_word == head_word or single_word == toks[-1]:
            return False  # the single word is the head word itself → same entity, absorb
        return True

    # S4: a chain of pure inflection/possessive suffixes (approximate, PERMISSIVE). Being permissive
    # is the safe direction: if the extension counts as a suffix there is no veto = old behavior kept.
    _EK_ZINCIRI = re.compile(
        r"(?:lar|ler|[yns]?[ıiuü]|[yn]?[ae]|[dt][ae]n?|n?[ıiuü]n|nd[ae]n?|yl[ae]|l[ae]|k[iı])+"
    )

    def _gecerli_gecis_sayisi(self, pattern, alt, metin, tek_kelime_map, kendi_karakteri):
        """S4 count fix (shadow prefix): stops the 'polly' pattern from counting
        'pollyanna' tokens and the 'kral' pattern from counting 'kraliçe' tokens.
        Rule: matched token = alt + extension; if the extension is NOT a pure suffix
        chain and the token is explained by a longer single-word variant of ANOTHER
        group (longest known variant wins), the match is not counted. Pure suffix
        extensions ('oduncunun', 'kızın') are exempt; the owner is the same entity."""
        sayi = 0
        for m in re.finditer(pattern, metin):
            eslesen = m.group(0)
            ek = eslesen[len(alt):]
            if ek and not self._EK_ZINCIRI.fullmatch(ek):
                baskasinin = False
                for v2, sahip in tek_kelime_map.items():
                    if sahip != kendi_karakteri and len(v2) > len(alt) and eslesen.startswith(v2):
                        baskasinin = True
                        break
                if baskasinin:
                    continue
            sayi += 1
        return sayi

    def should_add_to_group(self, modifier, group_modifier):
        return self.is_sublist_or_subset(modifier, group_modifier) or self.is_sublist_or_subset(group_modifier, modifier)

    def create_groups(self,phrase_list):
        subgroups = []
        for phrase in phrase_list:
            words = phrase.split()
            modifier = words[:-1]

            added = False
            for grup in subgroups:
                grup_modifier = grup[0].split()[:-1]
                if self.should_add_to_group(modifier, grup_modifier):
                    grup.append(phrase)
                    added = True
                    break

            if not added:
                subgroups.append([phrase])
        return subgroups

    def group_similars_by_head_word(self,phrases, nlp):
        head_group_dict = defaultdict(list)
        for phrase in phrases:
            head = self.get_head_word(phrase)
            head_group_dict[head].append(phrase)

        groups = []
        for head_lemma, phrase_list in head_group_dict.items():
            phrase_list = sorted(phrase_list, key=lambda x: (len(x.split()), x))
            subgroups = self.create_groups(phrase_list)

            for group in subgroups:
                character = min([x for x in group if len(x.split()) == max(len(y.split()) for y in group)], key=lambda x: len(x)) 
                groups.append({
                    "cekirdek": head_lemma,
                    "karakter": character,
                    "gruplar": [group]
                })

        return groups    

    def merge_single_word_character(self, group1_index, character1, matched_characters, copy, visited_groups, character_count, group1):
        dd=0
        for j, group2 in enumerate(copy):
            if j in visited_groups or group1_index == j:
                continue

            character2 = group2["karakter"]
            head_word_2 = self.get_head_word(character2)

            if character1 in character2.split() and not self._iyelik_sahibi_mi(character1, character2, head_word_2):
                dd=1
                # Single-word character occurs inside the other character
                # (P1 guard: the possessor side of a possessive phrase is not absorbed)
                matched_characters.append((j, character2, character_count.get(character2, 0)))
            else:
                # If the head words are similar
                if get_close_matches(character1, [head_word_2], cutoff=0.817):
                    matched_characters.append((j, character2, character_count.get(character2, 0)))

        if matched_characters and dd==1:
            most_frequent = max(matched_characters, key=lambda x: x[2])
            j, character2, _ = most_frequent

            copy[j]["gruplar"][0].extend(group1["gruplar"][0])
            character_count[character2] = character_count.get(character2, 0) + character_count.get(character1, 0)
            visited_groups.add(group1_index)
        elif matched_characters and dd==0:
            # Find the most frequent character
            most_frequent = max(matched_characters, key=lambda x: x[2])
            j, character2, _ = most_frequent

            count1 = character_count.get(character1, 0)
            count2 = character_count.get(character2, 0)

            # Add the less frequent character's group to the more frequent one
            if count1 <= count2:
                # group1 → group2
                copy[j]["gruplar"][0].extend(group1["gruplar"][0])
                character_count[character2] = count1 + count2
                visited_groups.add(group1_index)
            else:
                # group2 → group1
                group1["gruplar"][0].extend(copy[j]["gruplar"][0])
                character_count[character1] = count1 + count2
                visited_groups.add(j)


    def merge_similar_names_by_threshold(self, group1_index, character1, copy, visited_groups, character_count, merged_group, all_similars, threshold):
        for j in range(group1_index + 1, len(copy)):
            if j in visited_groups:
                continue

            group2 = copy[j]
            character2 = group2["karakter"]

            if character1 != character2 and get_close_matches(character1, [character2], cutoff=threshold):
                merged_group.extend(group2["gruplar"][0])
                all_similars.append((character2, character_count.get(character2, 0)))
                visited_groups.add(j)

            
    def merge_similar_named_groups(self, groups, character_count, threshold):
        new_groups = []
        groups_copy = groups.copy()
        visited_groups = set()

        for i, group1 in enumerate(groups_copy):   # check single-word characters first
            if i in visited_groups:
                continue

            character1 = group1["karakter"]
            if len(character1.split()) == 1:   # if character1 is a single word
                matched_characters = []
                self.merge_single_word_character(i, character1, matched_characters, groups_copy, visited_groups, character_count, group1)

        for i, group1 in enumerate(groups_copy):  # normal similarity check
            if i in visited_groups:
                continue

            character1 = group1["karakter"]
            merged_group = group1["gruplar"][0].copy()
            all_similars = [(character1, character_count.get(character1, 0))]

            self.merge_similar_names_by_threshold(i, character1, groups_copy, visited_groups, character_count, merged_group, all_similars, threshold)

            most_frequently_mentioned_char = max(all_similars, key=lambda x: x[1])[0]  # pick the most frequent character
            total_mention = sum([sayi for _, sayi in all_similars])

            new_groups.append({
                "cekirdek": self.get_head_word(most_frequently_mentioned_char),
                "karakter": most_frequently_mentioned_char,
                "gruplar": [sorted(set(merged_group))],   # S3: deterministic order
                "geçiş_sayısı": total_mention
            })

        return new_groups
    
    def _extract_ner_characters(self, doc):
        for ent in doc.ents:
            clean_char = self.clean_word(ent.text)
            if ent.label_ == "PERSON" and len(ent.text) > 1:
                if clean_char not in self.characters and clean_char not in self.turkce_stopwords:
                    self.characters.add(clean_char)


    def _extract_subject_characters(self, doc):
        for token in doc:
            if token.dep_ in ["nsubj", "nsubjpass"] and token.pos_ in ["NOUN", "PROPN", "ADJ"]:
                verb = token.head
                if verb.pos_ == "VERB" and verb.lemma_ in self.insansi_eylemler:
                    phrase = self.get_modifier_chain(token)
                    if phrase:
                        # Odak 4: do not count it as a character if it is bare (single word, no compound) and blacklisted.
                        # Compounds ("kuyruklu yıldız", "kara fırtına") are NOT affected → kept.
                        words = phrase.split()
                        if len(words) == 1 and (phrase in self.non_karakter
                                                or self.clean_word(token.lemma_) in self.non_karakter):
                            continue
                        if all(word not in self.turkce_stopwords for word in words):
                            self.characters.add(phrase)
                    else:
                        clean_char = self.clean_word(token.lemma_)
                        if (clean_char not in self.characters and clean_char not in self.turkce_stopwords and len(clean_char) > 1):
                            self.characters.add(clean_char)
    
    def _assign_sentences_to_groups(self, doc, group, sentences, tek_kelime_map=None):
        main_char = group["karakter"]
        alternatives = set()
        for sub_group in group["gruplar"]:
            alternatives.update(sub_group)
        alternatives = sorted(alternatives, key=lambda x: (-len(x), x))   # S3: tie-break for equal length

        patterns = [r'\b' + re.escape(alt) + r'([a-zçğıöşü]{0,6})?\b' for alt in alternatives]
        tek_kelime_map = tek_kelime_map or {}

        for sent in sentences:
            sent_text = sent.text
            sent_lower = sent_text.lower()
            candidates = []

            for token in sent:
                if token.pos_ in ["NOUN", "PROPN", "ADJ"]:
                    raw = self.get_modifier_chain(token) or token.text
                    cleaned = self.clean_word(raw)
                    candidates.append(cleaned)

            for alt, pattern in zip(alternatives, patterns):
                # S4: search and count go through the shadow-prefix veto (_gecerli_gecis_sayisi)
                if any(self._gecerli_gecis_sayisi(pattern, alt, candidate, tek_kelime_map, main_char) > 0
                       for candidate in candidates):
                    self.sentences_by_character[main_char].append(sent_text.strip())
                    self.character_counter[main_char] += self._gecerli_gecis_sayisi(
                        pattern, alt, sent_lower, tek_kelime_map, main_char)
                    break


    def tum_islemler(self):
        with open(self.path, "r", encoding="utf-8") as file:
            sentence = file.read()

        sentence = self.text_preprocess(sentence)
        doc = self.nlp(sentence)


        self._extract_ner_characters(doc)
        self._extract_subject_characters(doc)

        print("Karakterler:")
        for character in self.characters:
            print(character)
        print("--------------------")

        karakter_listesi = sorted(self.characters)   # S3: set order changed between runs

        groups = self.group_similars_by_head_word(karakter_listesi, self.nlp)

        
        print("\nGruplandırılmış Karakter Tamlamaları (Çekirdek Kelimeye Göre):")
        for i, group in enumerate(groups, 1):
            print(f"Grup {i}: {group}")

        sentences = list(doc.sents)

        # S4: single-word variant map of all groups (for the shadow-prefix veto).
        # When 'pollyanna' is in another group, the 'polly' pattern does not count it.
        tek_kelime_map = {}
        for group in groups:
            for sub_group in group["gruplar"]:
                for form in sub_group:
                    if " " not in form:
                        tek_kelime_map[form] = group["karakter"]

        for group in groups:
            self._assign_sentences_to_groups(doc, group, sentences, tek_kelime_map)


        # Printing
        print("\nKarakter Geçiş Sayıları:")
        for character, count in self.character_counter.items():
            print(f"{character}: {count}")

        groups = self.merge_similar_named_groups(groups, self.character_counter, threshold=0.817)
        print("\nbirleştirme:")
        for i, group in enumerate(groups, 1):
            print(f"Grup {i}: {group}")

        print("\nBirleştirilmiş Gruplar (Geçiş Sayılarıyla):")
        for i, group in enumerate(groups, 1):
            print(f"Grup {i}: Karakter = {group['karakter']} | Geçiş Sayısı = {group['geçiş_sayısı']}")
            print(f"  → Gruplar: {group['gruplar'][0]}")

        # Sort by mention count (descending) and print
        print("\nBirleştirilmiş Gruplar (Geçiş Sayılarıyla, Sıralı):")
        # Mention threshold = 4 (knee criterion, not the F1 peak). Curve: t5→t4 recall +4.6,
        # 6 characters recovered, only +2 noise FP; at t3/t2 the noise explodes.
        sirali_gruplar = sorted([g for g in groups if g["geçiş_sayısı"] >= 4], key=lambda x: x["geçiş_sayısı"], reverse=True)
        for i, group in enumerate(sirali_gruplar, 1):
            print(f"Karakter = {group['karakter']} | Geçiş Sayısı = {group['geçiş_sayısı']}")

        convert_sorted_groups = []
        for group in sirali_gruplar:
            character = group["karakter"]
            mention = group["geçiş_sayısı"]
            convert_sorted_groups.append((character, mention))


        with open("karakterler.txt", "w", encoding="utf-8") as f:
            for group in groups:
                if group["geçiş_sayısı"] >= 4:   # threshold = 4 (knee criterion)
                    ana_karakter = group["karakter"]
                    alternatifler = sorted(set(group["gruplar"][0]) - {ana_karakter})   # S3: line content is deterministic
                    satir = ",".join([ana_karakter] + alternatifler)
                    f.write(satir + "\n")    
        
        return convert_sorted_groups
    
# if __name__ == "__main__":
#     analiz = MetinAnaliz('NLP-Hikayeler\hikayeler\\ceviz.txt')
#     analiz.tum_islemler()
   