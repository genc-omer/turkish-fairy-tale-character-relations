from collections import Counter, defaultdict
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import networkx as nx
import matplotlib.pyplot as plt
import re
import spacy
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PyQt5.QtGui import QImage, QPixmap
import io

class CharacterRelations:
    def __init__(self, story_path, character_path="karakterler.txt"):
        self.model_name = "savasy/bert-base-turkish-sentiment-cased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.classifier = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
        self.nlp = spacy.load("tr_core_news_trf")
        
        self.story_path = story_path
        self.character_path = character_path
        self.variation_to_character = {}
        self.text = ""
        self.segments = []
        self.all_relations = []
        self.past_sentences = []
        self.pattern = re.compile(r'“[^“”]+”|"[^"]+"|[^“”".]+[.]')
        self.emotion_colors = {"positive": "green", "negative": "red", "neutral": "gray"}
        self.is_dialog = False

    def load_text(self):
        with open(self.story_path, "r", encoding="utf-8") as file:
            self.text = file.read()
            
        with open(self.character_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = [p.strip() for p in line.strip().split(",") if p.strip()]
                if parts:
                    main_character = parts[0]
                    for variation in parts:
                        self.variation_to_character[variation.lower()] = main_character
                        
    def split_sentence_dialog(self):
        for match in re.finditer(self.pattern, self.text):
            sentence = match.group().strip()
            if not sentence:
                continue
            self.is_dialog = (sentence.startswith("“") and sentence.endswith("”")) or (sentence.startswith('"') and sentence.endswith('"'))
            self.segments.append((sentence.strip("“”\""), self.is_dialog))

    def find_characters(self, sentence):
        sentence = sentence.lower()
        found = set()
        for variation, character in self.variation_to_character.items():
            pattern = r'\b' + re.escape(variation.lower()) + r'(?:[ınunıneoaüie]{0,4})?\b'
            if re.search(pattern, sentence):
                found.add(character)
        return list(found)

    def contains_pronoun(self, doc):
        return any(token.pos_ == "PRON" for token in doc)

    # Odak 1: hedef 3. şahıs zamir kümeleri (sayı uyumu için)
    _PRON_SINGULAR = {"o", "onu", "ona", "onun", "onda", "ondan", "onunla", "onunki"}
    _PRON_PLURAL = {"onlar", "onları", "onlara", "onların", "onlarda", "onlardan"}
    _PRON_REFLEX = {"kendi", "kendisi", "kendine", "kendini", "kendinden",
                    "kendisine", "kendisini", "kendileri"}

    def pronoun_number(self, doc):
        """Cümledeki özne/nesne konumundaki hedef zamirin sayısını döndür:
        'plural' / 'reflexive' / 'singular' / None. Öncelik: çoğul > refleksif > tekil."""
        has_p = has_r = has_s = False
        for tok in doc:
            if tok.pos_ != "PRON":
                continue
            w = tok.text.lower()
            if w in self._PRON_PLURAL:
                has_p = True
            elif w in self._PRON_REFLEX:
                has_r = True
            elif w in self._PRON_SINGULAR:
                has_s = True
        if has_p:
            return "plural"
        if has_r:
            return "reflexive"
        if has_s:
            return "singular"
        return None

    def find_previous_character(self, max_lookback=3, pronoun_number=None):
        candidates = []
        for sentence in reversed(self.past_sentences[-max_lookback:]):
            chars_in_sentence = self.find_characters(sentence)
            if chars_in_sentence:
                candidates.extend(chars_in_sentence)
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c not in seen:
                unique_candidates.append(c)
                seen.add(c)

        # ---- Odak 1: sayı uyumu + BELİRSİZSE ÇÖZME (yalnızca pronoun_number verildiğinde) ----
        if pronoun_number == "plural":
            # çoğul "onlar*": önceki bağlamdaki 2+ karakter grubu; <2 ise çözme
            return list(unique_candidates) if len(unique_candidates) >= 2 else None
        if pronoun_number == "reflexive":
            # refleksif "kendi/kendisi": cümlenin kendi öznesine döner → yeni çift üretmez
            return None
        if pronoun_number == "singular":
            # tekil: yalnızca TEK aday varsa çöz; belirsizse (≥2) ÇÖZME (precision guard)
            return unique_candidates[0] if len(unique_candidates) == 1 else None

        # ---- pronoun_number=None: GENEL linking / eski davranış aynen korunur ----
        if len(unique_candidates) == 1:
            return unique_candidates[0]
        for sentence in reversed(self.past_sentences[-max_lookback:]):
            doc = self.nlp(sentence)
            for token in doc:
                if token.dep_ == "nsubj":
                    word = token.text.lower()
                    for variation, character in self.variation_to_character.items():
                        if variation.lower() == word:
                            return character
        if unique_candidates:
            return unique_candidates[0]
        return None

    def establish_emotional_relation(self, sentence, characters, emotion, previous_character=None):
        relations = []
        
        if self.is_dialog:
            # In dialog:
            # If previous character exists, relate with all characters in dialog
            if previous_character:
                for target in characters:
                    if target != previous_character:
                        relations.append({"from": previous_character, "to": target, "emotion": emotion})
            
            #Characters in dialog can also relate among themselves
            if len(characters) >= 2:
                for i in range(len(characters)):
                    for j in range(i + 1, len(characters)):
                        if characters[i] != characters[j]:
                            relations.append({"from": characters[i], "to": characters[j], "emotion": emotion})
        
        else:
            #Not dialog, normal relation
            if len(characters) >= 2:
                for i in range(len(characters)):
                    for j in range(i + 1, len(characters)):
                        if characters[i] != characters[j]:
                            relations.append({"from": characters[i], "to": characters[j], "emotion": emotion})
            
            #If single character and previous character exists, relate them
            elif len(characters) == 1 and previous_character and characters[0] != previous_character:
                relations.append({"from": previous_character, "to": characters[0], "emotion": emotion})
        
        return relations

    def moving_average(self, data, window_size=5):
        return [sum(data[i:i+window_size])/window_size for i in range(len(data)-window_size+1)]

    def process(self):
        for i, (sentence, self.is_dialog) in enumerate(self.segments):
            doc = self.nlp(sentence)
            present_characters = self.find_characters(sentence)

            if not present_characters and self.contains_pronoun(doc):
                # Odak 1: zamirin sayısını tespit et, sayı uyumu + belirsizse-çözme uygula
                pron_num = self.pronoun_number(doc)
                resolved = self.find_previous_character(pronoun_number=pron_num)

                # belirsiz tekil / refleksif / yetersiz çoğul → çözme, ilişki kurma
                if resolved is None:
                    self.past_sentences.append(sentence)
                    continue

                resolved_list = resolved if isinstance(resolved, list) else [resolved]
                estimated_characters = list(resolved_list)
                if self.is_dialog:
                    next_character = None
                    for j in range(i + 1, len(self.segments)):
                        next_sentence, _ = self.segments[j]
                        next_chars = self.find_characters(next_sentence)
                        if next_chars:
                            next_character = next_chars[0]
                            break
                    if next_character and next_character not in estimated_characters:
                        estimated_characters.append(next_character)
                present_characters = estimated_characters

            if not present_characters:
                self.past_sentences.append(sentence)
                continue

            previous = self.find_previous_character()

            if len(present_characters) == 1 and not self.is_dialog:
                if not previous or present_characters[0] == previous:
                    self.past_sentences.append(sentence)
                    continue

            try:
                emotion = self.classifier(sentence)[0]["label"]
            except:
                self.past_sentences.append(sentence)
                continue

            relations = self.establish_emotional_relation(sentence, present_characters, emotion, previous)
            self.all_relations.extend(relations)
            self.past_sentences.append(sentence)

            
    def draw_emotion_curve(self) -> QPixmap:#Giriş gelişme sonuç bölümlerini ayırma ve grafiğini çizme
        emotion_scores = []
        label_to_score = {"positive": 1, "neutral": 0, "negative": -1}
        for relation in self.all_relations:
            emotion = relation["emotion"]
            score = label_to_score.get(emotion, 0)
            emotion_scores.append(score)

        smooth_emotion_flow = self.moving_average(emotion_scores, window_size=5)

        change_scores = [abs(smooth_emotion_flow[i] - smooth_emotion_flow[i - 1]) for i in range(1, len(smooth_emotion_flow))]
        if len(change_scores) < 2:
            raise ValueError("Not enough emotion data.")

        scores_copy = change_scores.copy()
        first_break = scores_copy.index(max(scores_copy)) + 1
        scores_copy[first_break - 1] = -1  

        min_distance = int(len(change_scores) * 0.15)

        second_break_candidates = [(i, val) for i, val in enumerate(scores_copy) if abs(i + 1 - first_break) >= min_distance]

        if second_break_candidates:
            second_break = max(second_break_candidates, key=lambda x: x[1])[0] + 1
        else:
            second_break = scores_copy.index(max(scores_copy)) + 1

        break_points = sorted([first_break, second_break])

        fig = plt.figure(figsize=(10, 4))
        plt.plot(smooth_emotion_flow, color='purple', linewidth=2)
        plt.axvline(x=break_points[0], color='gray', linestyle='--', label="Section Break")
        plt.axvline(x=break_points[1], color='gray', linestyle='--')
        plt.title("Emotion Curve (Moving Average)")
        plt.xlabel("Time (Sentence/Relation Order)")
        plt.ylabel("Emotion Score")
        plt.yticks([-1, 0, 1], ["Negative", "Neutral", "Positive"])
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        plt.close(fig)

        image = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(image)

        return pixmap


    def overall_relation_graph(self) -> QPixmap:
        relations_emotions = defaultdict(list)
        for relation in self.all_relations:
            c1, c2 = sorted([relation["from"], relation["to"]])
            relations_emotions[(c1, c2)].append(relation["emotion"])

        dominant_relations = {}
        for pair, emotions in relations_emotions.items():
            counts = Counter(emotions)
            dominant_emotion = counts.most_common(1)[0][0]
            dominant_relations[pair] = dominant_emotion

        G = nx.Graph()
        for (c1, c2), emotion in dominant_relations.items():
            G.add_node(c1)
            G.add_node(c2)
            G.add_edge(c1, c2, emotion=emotion)

        edge_colors = [self.emotion_colors.get(data['emotion'], 'black') for _, _, data in G.edges(data=True)]

        fig = plt.figure(figsize=(10, 7))
        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, edge_color=edge_colors, node_color='lightblue',
                node_size=2000, font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(G, 'emotion')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black')
        plt.title("Overall Fairy Tale Characters Emotional Relation Network")
        plt.axis('off')
        plt.tight_layout()

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        plt.close(fig)

        image = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(image)

        return pixmap

    def section_based_graph(self, title=None) -> QPixmap:
        from sklearn.metrics import pairwise_distances
        import numpy as np

        emotions_sequence = [relation["emotion"] for relation in self.all_relations]
        n_emotions = len(emotions_sequence)
        
        if n_emotions < 3:
            raise ValueError("Not enough relation data (at least 3 required)")

        unique_emotions = list(set(emotions_sequence))
        emotion_to_idx = {emotion: i for i, emotion in enumerate(unique_emotions)}
        vectors = [emotion_to_idx[e] for e in emotions_sequence]

        change_scores = [abs(vectors[i] - vectors[i - 1]) for i in range(1, len(vectors))]

        scores_copy = change_scores.copy()
        first_break = scores_copy.index(max(scores_copy)) + 1
        scores_copy[first_break - 1] = -1
        second_break = scores_copy.index(max(scores_copy)) + 1

        break_points = sorted([first_break, second_break])

        section1 = self.all_relations[:break_points[0]]
        section2 = self.all_relations[break_points[0]:break_points[1]]
        section3 = self.all_relations[break_points[1]:]

        sections = {
            "Giriş Bölümü": section1,
            "Gelişme Bölümü": section2,
            "Sonuç Bölümü": section3
        }

        if title not in sections:
            raise ValueError("Invalid section title. Must be 'Introduction', 'Development', or 'Conclusion'.")

        section = sections[title]

        relations_emotions = defaultdict(list)
        for relation in section:
            c1, c2 = sorted([relation["from"], relation["to"]])
            relations_emotions[(c1, c2)].append(relation["emotion"])

        dominant_relations = {}
        for pair, emotions in relations_emotions.items():
            counts = Counter(emotions)
            dominant_emotion = counts.most_common(1)[0][0]
            dominant_relations[pair] = dominant_emotion

        G = nx.Graph()
        for (c1, c2), emotion in dominant_relations.items():
            G.add_node(c1)
            G.add_node(c2)
            G.add_edge(c1, c2, emotion=emotion)

        edge_colors = [self.emotion_colors.get(data['emotion'], 'black') for _, _, data in G.edges(data=True)]

        fig = plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, edge_color=edge_colors, node_color='lightblue',
                node_size=2000, font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(G, 'emotion')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black')
        plt.title(f"{title} Emotional Relation Network")
        plt.axis('off')
        plt.tight_layout()

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        plt.close(fig)

        image = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(image)

        return pixmap


# if _name_ == "_main_":
#     relations = CharacterRelations("NLP-Hikayeler/hikayeler/zehrakisahikaye.txt")
#     relations.load_text()
#     relations.split_sentence_dialog()
#     relations.process()
#     relations.draw_emotion_curve()
#     relations.overall_relation_graph()
#     relations.section_based_graph("Introduction")