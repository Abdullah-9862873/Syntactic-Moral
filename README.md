# Syntactic Morality Analyzer

## What's This App? (Like Explaining to a Kid)

Imagine you have a robot that can read text and understand if someone is talking about being nice, fair, or loyal to others. That's what this app does!

**It's like a feelings detective for words.** When someone writes something, this app checks:
- Are they talking about caring for someone? 🧡
- Are they being fair? ⚖️
- Are they loyal to their friends or group? 🤝
- Are they showing respect to authority? 👑

---

## Why Did I Build This?

I was reading about something called "moral foundations" - these are big ideas that all humans care about, like:
- **Care/Help** - Are we being kind?
- **Fairness** - Is everyone treated equally?
- **Loyalty** - Do we stick with our friends?
- **Authority** - Do we respect leaders?

The problem was: simple word counting didn't work well. If someone said "I am NOT caring" the old system would think they ARE caring (because it saw the word "caring"). That's wrong!

So I built a smarter system that:
1. Understands when words are negated ("not", "never", etc.)
2. Knows who is doing what to whom (grammar!)
3. Handles tricky phrases like "not only...but also"

---

## Problems I Fixed

### Problem 1: "Not" Doesn't Always Mean No
- **Before:** "I am not caring" → showed NO moral detection at all 😢
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

### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
python run_app.py
```

### Step 3: Open in Browser
Go to: http://localhost:8501

---

## How to Test

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

## Files in This Project

```
SyntacticMoral/
├── backend/
│   ├── data/           # Dictionary files (MFD, eMFD, eMACD)
│   ├── pipeline/       # Core scoring logic
│   └── tests/         # Automated tests
├── frontend/
│   └── app.py         # Streamlit web app
├── images/            # Screenshots
├── docs/              # Documentation
└── research_summary.pdf  # For professors
```

---

## For Researchers

If you want to cite this work:

> Sultan, A. (2026). Syntactic Morality Analyzer: Extending eMACD with Syntactic Analysis. 
> Based on Weber Lab (UCSB) and Malik et al. (2025) eMACD paper.

---

## Contact

- Abdullah Sultan
- Fall 2027 PhD Applicant
- Email: ag9862873@gmail.com

---

## Acknowledgments

Thank you to:
- **Professor Rene Weber** (UCSB) - Media Neuroscience Lab
- **Musa Malik** (UCSB) - Lead for eMACD paper
- The eMACD, eMFD, MFD research teams