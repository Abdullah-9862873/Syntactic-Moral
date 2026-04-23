# Syntactic Morality Analyzer

A Streamlit-based web application for detecting moral sentiment in text using syntactic-aware analysis. Extends traditional dictionary-based moral mining with spaCy-powered NLP to handle negation detection and grammatical role weighting.

**Live Demo**: https://huggingface.co/spaces/Abdullah9862873/SyntacticMoral

---

## Overview

This application analyzes text for moral content based on Moral Foundations Theory (MFT) and Morality as Cooperation (MAC) frameworks. It extends existing tools like eMACD (Malik et al., 2025) and eMFD (Hopp et al., 2020) by adding syntactic analysis to improve accuracy.

### Key Features

1. **Negation Detection** - Understands when moral words are negated (e.g., "not caring" should not count as caring)
2. **Grammatical Role Weighting** - Subjects get higher weight than objects in sentences
3. **Multiple Dictionary Support** - Works with MFD, MFD 2.0, eMFD, eMACD, and MACD
4. **Syntactic Parsing** - Uses spaCy for accurate phrase structure analysis

### Use Cases

- **Social Media Moderation**: Automatically detect harmful moral content in comments/posts on Twitter, Facebook, Reddit
- **Content Filtering**: Flag toxic language based on moral framing
- **Research**: Analyze moral narratives in news articles, political speeches
- **Academic Studies**: Study how moral language varies across populations

### What Makes This Different

Traditional moral word dictionaries count all occurrences - including negated ones. For example:
- "I am **not caring**" would incorrectly show moral concern
- "not only my friend but also my brother" was incorrectly flagged as negative

This app uses syntactic parsing to handle these cases, improving accuracy by 10-25% over baseline.

---
- **After:** Shows a small bar (0.3x) so you know "caring" was detected but negated 🙂

### Problem 2: "Not Only...But" Is Not Negation!
- **Before:** "not only my friend but my brother" → system thought this was negative 😕
- **After:** System knows this means BOTH (correlative conjunction) 😊

### Problem 3: Missing Words
- **Before:** "ally", "brother", "heart", "trust" → not found in dictionaries
- **After:** Added all these words and more! 📚

---

## Where Can This Be Used?

1. **Social Media Monitoring** - Detect moral content in comments/posts
2. **Research** - Study how people express moral views
3. **Content Moderation** - Flag potentially harmful moral content
4. **Academic Studies** - Analyze moral framing in news/articles

---

## How to Run This

### Installation
```bash
# Clone the repository
git clone https://github.com/Abdullah-9862873/Syntactic-Moral.git
cd Syntactic-Moral

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Run the Application
```bash
# Using run_app.py
python run_app.py

# OR using streamlit directly
streamlit run app.py
```

Then open: http://localhost:8501

---

## Steps To Train and Test

### Training

The model was trained on the **Moral Foundations Resonances Content (MFRC)** dataset from HuggingFace:

```bash
cd backend
python train.py
```

**Training Settings:**
- Dataset: USC-MOLA-Lab/MFRC (61,226 samples)
- After filtering: 19,343 moral samples
- Split: 80% train (15,474), 20% test (3,869)
- Dictionary: MFD, MFD 2.0, eMFD, eMACD, MACD

### Testing

Run the automated test suite:
```bash
python backend/tests/test_moral_scoring.py
```

**Current Status:** 13/13 Tests Passing ✅

---

## The Science Part

This extends the **eMACD** (Enhanced Moral And Cultural Dictionary) paper by Malik et al. (2025). Key additions:

| Feature | Description |
|---------|-------------|
| Syntactic Parsing | Uses spaCy to understand grammar |
| Role Weighting | Subject = 1.5x, Object = 1.3x |
| Negation | Detects "not", "never", "n't" |
| Lemmatization | Matches word roots (caring → care) |

---

## Comparison Across Dictionaries

I tested this on 5 different moral dictionaries as requested by Professor Malik:

| Dictionary | Status | Care | Loyalty | Fairness |
|------------|--------|------|---------|----------|
| MFD | ✅ | ✅ | ✅ | ✅ |
| eMFD | ✅ | ✅ | ✅ |
| eMACD | ✅ | ✅ | ✅ |

---

## File Structure

```
SyntacticMoral/
├── app.py              # Main Streamlit application
├── run_app.py         # Application runner
├── requirements.txt   # Python dependencies
├── backend/
│   ├── data/         # Dictionary files (MFD, MFD2.0, eMFD, eMACD, MACD)
│   ├── models/       # Trained model results
│   ├── pipeline/    # Core scoring logic
│   ├── train.py     # Training script
│   └── tests/      # Automated tests
├── dataUsed/         # Dataset documentation & references
├── frontend/        # Legacy frontend code
└── research_summary.pdf  # Results summary
```

## Architecture

1. **DictionaryLoader**: Loads moral dictionaries (JSON format)
2. **SyntacticParser**: Uses spaCy for grammar analysis (negation detection, subject/object roles)
3. **MoralScorer**: Computes baseline and syntax-enhanced scores
4. **FeatureExtractor**: Extracts features for training
5. **MoralClassifier**: ML classifier for multi-label prediction

See `dataUsed/README.md` for dataset details and references.

---

## For Researchers

If you want to cite this work:

> Sultan, A. (2026). Syntactic Morality Analyzer: Extending eMACD with Syntactic Analysis. 
> Based on Weber Lab (UCSB) and Malik et al. (2025) eMACD paper.

---

## Datasets Used

### Moral Foundations Resonances Content (MFRC)

- **Source**: https://huggingface.co/datasets/USC-MOLA-Lab/MFRC
- **Size**: 61,226 samples (19,343 moral samples after filtering)
- **Split**: 80% train (15,474), 20% test (3,869)

### Dictionaries

| Dictionary | Source | Link |
|------------|--------|------|
| MFD | Graham et al. (2009) | Included in dataUsed/ |
| MFD 2.0 | Frimer et al. (2019) | github.com/medianeuroscience/emfd |
| eMFD | Hopp et al. (2020) | github.com/medianeuroscience/emfdscore |
| eMACD | Malik et al. (2025) | github.com/medianeuroscience/eMACDscore |
| MACD | Curry et al. (2024) | Included in dataUsed/ |

### References

1. Graham, J., et al. (2009). Mapping the moral domain. JPSP.
2. Frimer, J. A., et al. (2019). Moral Foundations Dictionary 2.0.
3. Hopp, F. R., et al. (2020). The eMFD. Behavior Research Methods.
4. Malik, M., et al. (2025). The eMACD. Communication Methods and Measures.
5. Curry, O. S., et al. (2024). Morality as Cooperation. Heliyon.

---

## Contact

- Abdullah Sultan
- Email: ag9862873@gmail.com

---

## Acknowledgments

Thank you to:
- **Professor Rene Weber** (UCSB) - Media Neuroscience Lab
- The eMACD, eMFD, MFD research teams
