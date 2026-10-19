# Character and Relationship/Sentiment Analysis in Turkish Fairy Tales

An end-to-end system that automatically extracts **characters** and the **sentiment polarity (positive / negative) of the relationships between them** from Turkish fairy-tale texts. Results are visualized as a character relationship network and a sentiment-progression curve over the story.

> Yıldız Technical University · Department of Computer Engineering · Undergraduate Interim Project
> **Authors:** Ömer Genç, Erdem Açıkel  ·  **Advisor:** Prof. Dr. Banu Diri

---

## Method

The system is a two-branch pipeline and uses **pre-trained, off-the-shelf models; no model was trained in this project.**

- **Pre-processing + NLP:** sentence splitting and named-entity recognition (NER) with spaCy `tr_core_news_trf`.
- **Character branch:** the NER output is passed through a subject-based filter, and different mentions of the same character are merged under a single canonical name → character list.
- **Relationship branch:** pronouns are resolved, character pairs co-occurring in the same sentence are found, and the sentence sentiment is labeled with `savasy/bert-base-turkish-sentiment-cased` (binary: positive / negative) → relationship and its polarity.
- **Visualization:** relationship network and sentiment-progression curve with NetworkX + Matplotlib; PyQt5 desktop interface.

---

## Installation and Usage

Development environment: **Python 3.10** (tested with 3.10.11).

```bash
# 1) (Recommended) virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 2) Dependencies
pip install -r requirements.txt

# 3) spaCy Turkish model + NLTK data
python -m spacy download tr_core_news_trf
python -c "import nltk; nltk.download('punkt')"

# 4) Launch the application (opens the PyQt5 interface)
python main.py
```

In the interface: click **"Hikaye Seç"** (Select Story) to choose a `.txt` fairy-tale file → click **"Analiz Et"** (Analyze) to start. The character/relationship list, the relationship network, and the **"Duygu Değişimi Grafiği"** (Sentiment Change Graph) are displayed.

> On first run, the spaCy (`tr_core_news_trf`) and BERT (`savasy`) models are downloaded from the internet; an active connection is required.

---

## Data

- **25 Turkish fairy tales** (~2236 sentences).
- Manually annotated **gold standard**: **130 characters** (45 main), **146 relationships** (102 positive / 36 negative / 8 neutral).
- Annotation criteria: [`ANNOTATION_RULES.md`](test_data/annotations/ANNOTATION_RULES.md) (rules K1–K11).

---

## Results

On the same frozen gold standard (values in %):

| Task          | Set  | P     | R    | Micro-F1 | Macro-F1 |
|---------------|------|-------|------|----------|----------|
| Character     | Main | 86.7  | 86.7 | **86.7** | 88.7     |
| Character     | All  | 82.8  | 73.8 | **78.0** | 78.6     |
| Relationship  | Main | 100.0 | 86.4 | **92.7** | 60.0     |
| Relationship  | All  | 51.9  | 64.4 | **57.5** | 61.0     |

Example (outside the evaluation set): “Cesur Ayşe”. A short tale that is not among the 25 evaluated tales, included in `examples/` as a quick demo. On it, the system finds all 4 characters (Ayşe, Zeynep, Mert, Demir) and all 6 relationships with the same polarities as our hand annotation.

---

## Limitations (stated honestly)

- **The sentiment model is binary** (positive/negative only); it cannot produce a neutral label, so neutral relationships in the gold set are excluded from the polarity measurement.
- **Polarity is the weakest stage: 42.0%** (positive 42.2%, negative 41.7%). The core limitation is structural (a *construct gap*): the **surface sentiment** of a sentence does not always match the **actual relationship** between characters; the predominantly sad tone of fairy tales can make positive relationships read as negative.
- Different names of the same character (**aliases**) are sometimes treated as separate, leading to spurious relationships (the main reason for the drop on the all-character set).
- **The dataset is small** (25 tales).

---

## Interface Preview

![interface](https://github.com/user-attachments/assets/f2010a98-4079-465d-a07c-32f994b041fa)

---

## Notes

- Input `.txt` files must be UTF-8 encoded and written in Turkish.
- This repository contains the application code, the dataset (`NLP-Hikayeler/`), and the gold standard (`test_data/`). Generated output files (predictions / metrics / logs) are excluded via `.gitignore` and can be regenerated with `run_baseline.py` / `evaluation.py`.
