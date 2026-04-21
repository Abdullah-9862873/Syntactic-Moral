# Implementation Plan: Syntactic Morality Analyzer

## Project Overview

This document outlines the implementation plan for the Syntactic Morality Analyzer, an extension to eMACD score with syntactic analysis. The project aims to improve moral content detection in text using dictionary-based approaches enhanced with syntactic parsing, addressing issues like negation handling and correlative conjunctions.

---

## 1. Current Status

### 1.1 What's Done ✅

| Component | Status | Details |
|-----------|--------|---------|
| Backend Pipeline | ✅ Complete | Syntactic parser, scorer, dictionaries |
| Training Code | ✅ Complete | Configured for 61,226 samples |
| Training Results | ✅ Available | In `backend/models/results_summary.txt` |
| Web UI | ✅ Complete | Streamlit app with syntax analysis |
| README | ✅ Complete | Kid-friendly explanation |
| Documentation | ✅ Complete | In `docs/fix-documentation.md` |

### 1.2 Training Results (from 15K samples)

| Dictionary | Baseline F1 | Syntax F1 | Improvement |
|------------|-------------|-----------|--------------|
| MFD | 0.352 | 0.467 | +11.5% |
| MFD2 | 0.234 | 0.458 | +22.5% |
| eMFD | 0.348 | 0.464 | +11.6% |
| **eMACD** | **0.000** | **0.443** | **+44.3%** |
| MACD | 0.234 | 0.458 | +22.5% |

---

## 2. What's Missing & Implementation Plan

### 2.1 Run Training on Full 61K Samples

**Status:** Code ready, not executed

**Action:**
```bash
cd SyntacticMoral && python backend/train.py
```

**Expected:** Better F1 scores with more training data

---

### 2.2 Clean Up Code

**Issues:**
1. `train.py` - Has progress bar import but needs cleanup
2. `classifier.py` - Has LSP errors (pre-existing)
3. Duplicate code in train.py loops

**Action:** Clean up syntax errors

---

### 2.3 Research Summary PDF Generation

**Status:** Need to create proper generate_pdf.py

**Reference Images (from `Project/images/`):**
- `1.png` - Performance chart
- `2.png` - Confusion matrix
- `3.png` - Improvement bars
- `4.png` - Dataset distribution
- `5.png` - Role weights
- `6.png` - Per-foundation results
- `7.png` - Summary statistics

**Action:** Update `generate_pdf.py` to use these images with descriptions

---

### 2.4 Update Research Summary with Training Results

**Content to Include:**

1. **Title:** Syntactic Morality Analyzer: Extending eMACD with Syntactic Analysis

2. **Abstract:** 
   - Problem: Keyword matching doesn't handle negation or grammatical roles
   - Solution: Add syntactic parsing with spaCy
   - Results: +11% to +44% improvement across dictionaries

3. **Introduction:**
   - Reference Prof. Musa Malik's email requesting multi-dictionary testing
   - Quote: "Could you repeat the same analyses across MFD, MFD 2.0, eMFD lexicons?"

4. **Methods:**
   - Dataset: MFRC (61,226 samples from HuggingFace)
   - NLP: spaCy en_core_web_sm
   - Classifiers: Logistic Regression per domain
   - Features: TF-IDF + syntactic roles

5. **Results:**
   - Include tables from training results
   - Show images 1-7 from Project/images folder

6. **Discussion:**
   - Key insight: Syntax helps across ALL dictionaries
   - eMACD shows biggest improvement (+44%)
   - Negation handling now shows bars

7. **Conclusion:**
   - Syntactic analysis enhances moral detection
   - Works for both MFT and MAC dictionaries

---

## 3. Implementation Steps

### Step 1: Fix Code Issues
- [ ] Remove duplicate loop code in train.py
- [ ] Fix syntax errors

### Step 2: Run Full Training
- [ ] Run `python backend/train.py` with 61K samples
- [ ] Verify results improve

### Step 3: Generate Research PDF
- [ ] Update generate_pdf.py to use Project/images references
- [ ] Add training results to PDF
- [ ] Generate final research_summary.pdf

### Step 4: Final Review
- [ ] Check README is complete
- [ ] Verify all features work
- [ ] Prepare for GitHub commit

---

## 4. File Structure

```
SyntacticMoral/
├── backend/
│   ├── data/
│   │   ├── mfd.json          # Moral Foundations Dictionary
│   │   ├── emfd.json        # Extended MFD
│   │   ├── emacd.json      # Enhanced MACD
│   │   └── macd.json       # MACD
│   ├── pipeline/
│   │   ├── dictionaries.py  # Dictionary loader
│   │   ├── syntactic_parser.py  # spaCy parsing
│   │   ├── scorer.py     # Scoring with syntax
│   │   ├── classifier.py # Training
│   │   └── features.py # Feature extraction
│   ├── models/
│   │   ├── multi_dict_results.json
│   │   └── results_summary.txt
│   └── train.py           # Training script
├── frontend/
│   └── app.py           # Streamlit web app
├── images/                 # Screenshot images
├── docs/
│   └── fix-documentation.md
├── research_summary.pdf    # Generated PDF
├── README.md           # Project README
├── requirements.txt
└── run_app.py         # App launcher
```

---

## 5. Research Summary PDF Content

Based on the structure in `Project/images/`, the final research_summary.pdf should include:

### Page Layout (per images 1-7):

**Image 1: Title & Abstract**
- Title: Syntactic Morality Analyzer
- Subtitle: Extending eMACD with Syntactic Analysis
- Abstract paragraph

**Image 2: Introduction**
- Professor's request (Musa Malik email)
- Research question
- Why this matters

**Image 3: Methods**
- Dataset info (MFRC, 61K samples)
- NLP model (spaCy)
- Training configuration

**Image 4: Results Table**
- Multi-dictionary comparison table
- All 5 dictionaries with F1 scores

**Image 5: Before/After**
- Example sentences
- Negation handling
- Correlative detection

**Image 6: Detailed Results**
- Per-foundation breakdown
- Charts from training

**Image 7: Conclusion**
- Key takeaways
- Future work
- References

---

## 6. Running the Project

### Quick Start:
```bash
# Install requirements
pip install -r requirements.txt

# Run training (optional - results already exist)
python backend/train.py

# Run web app
python run_app.py

# Generate research PDF
python generate_pdf.py
```

### Web App:
- Open browser to http://localhost:8501
- Select dictionary (MFD, eMFD, eMACD, etc.)
- Enter text to analyze
- View results with matched words and bars

---

## 7. Key Technical Details

### Syntactic Features:
- **Role Weighting:** Subject=1.5x, Object=1.3x, Modifier=0.8x
- **Negation:** 0.3x weight (shows bars even when negated)
- **Correlative:** "not only...but" detected as non-negative

### Dictionaries Tested:
- MFD (Graham et al., 2013)
- MFD 2.0
- eMFD (Hopp et al., 2021)
- eMACD (Malik et al., 2025)
- MACD (Curry et al., 2019)

### Performance:
- Best improvement: eMACD (+44.3%)
- Average improvement: +22%
- All dictionaries improved with syntax

---

## 8. Research Context

Based on emails with professors:

**Prof. Musa Malik said:**
> "Could you repeat the same analyses across MFD, MFD 2.0, eMFD lexicons? I am curious to see if variations across MFT dictionaries increase baseline lexicon effects."

**This project answers:**
- ✅ Tested across ALL 5 dictionaries
- ✅ Found varying baseline effects (eMACD: 0%, others: 23-35%)
- ✅ Showed syntax helps all dictionaries

---

## 9. Next Steps Summary

| Task | Priority | Status |
|------|----------|--------|
| Fix code errors | High | Pending |
| Run 61K training | Medium | Not Done |
| Update PDF generator | High | Pending |
| Generate final PDF | High | Pending |
| Final review | Medium | Pending |

---

## 10. Contact

- **Developer:** Abdullah Sultan
- **Email:** ag9862873@gmail.com
- **GitHub:** github.com/Abdullah-9862873/Syntactic-Moral
- **Year:** 2026

---

*This implementation plan was created to guide the completion of the Syntactic Morality Analyzer project for submission to UCSB Media Neuroscience Lab (Prof. Rene Weber and Musa Malik).*