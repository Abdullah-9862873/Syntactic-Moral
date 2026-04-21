# Syntactic Morality Analyzer

An extension to eMACDscore that adds syntactic weighting to detect negation and grammatical roles in moral text classification.

## What Is This App?

**This app is like a smart robot that reads sentences and guesses if they are talking about morals or not!**

### Think of it like a game:

Imagine you have a list of "good words" and "bad words":
- If someone says "kind" → sounds good!
- If someone says "fair" → sounds good!
- If someone says "cheat" → sounds bad!

This app has **5 different word lists** (called dictionaries) to test:

| Dictionary | Full Name | Research Paper |
|------------|-----------|---------------|
| **MFD** | Moral Foundations Dictionary | Graham et al. (2013) |
| **MFD 2.0** | Moral Foundations Dictionary 2.0 | Graham et al. (updated) |
| **eMFD** | extended Moral Foundations Dictionary | Hopp et al. (2021) |
| **eMACD** | extended Morality as Cooperation Dictionary | Malik et al. (2025) |
| **MACD** | Morality as Cooperation Dictionary | Curry et al. (2019) |

### Why so many lists?

Different researchers wrote different "good word" lists:
- **MFT lists (MFD, MFD 2.0, eMFD)** → Focus on: Care, Fairness, Loyalty, Authority, Purity, Equality
- **MAC lists (eMACD, MACD)** → Focus on: Family, Heroism, Reciprocity, Fairness

Researchers compare which list works better!

### What does "Syntactic" mean?

This is the special magic part! It's not just counting words - it understands **grammar**:

#### Example:
> "I **don't** care about fairness"

- **Basic app**: Sees "care" and "fairness" → says "Moral!" ❌
- **Syntactic app**: Sees "don't" (negation!) → understands "I DON'T care" → says "Not moral!" ✅

### How it works:
1. **Subject** (who is doing something) → gets **more weight**
2. **Negation words** (not, never, no) → **reduce the score**
3. **Object** (what is being done to) → gets some weight

## Research Inspiration

This project was inspired by the following research:

- **Prof. René Weber** - UCSB Media Neuroscience Lab
  - Research: Moral reasoning in media and neural mechanisms of moral conflict
  - https://medianeuroscience.org

- **Musa Malik** - UCSB Media Neuroscience Lab
  - Paper: eMACD - extended Morality as Cooperation Dictionary (2025)
  - Research: Platform-based moral annotation across media formats

- **F. R. Hopp et al.** - eMFD (2021)
  - Paper: Moral foundations dictionary extended

- **J. Graham et al.** - MFD 2.0 (2013)
  - Paper: Moral Foundations Dictionary

- **T. Curry et al.** - MACD (2019)
  - Paper: Morality as Cooperation Dictionary

## Quick Start

### Prerequisites

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
python -m spacy download en_core_web_sm
```

### Run the App

```bash
python run_app.py
```

### Run Training

```bash
cd backend
python train.py
```

This trains models on all 5 dictionaries and generates comparison results.

## In Simple Terms

| Word | Meaning |
|------|---------|
| **Morality** | What's right and wrong, good and bad |
| **Dictionary** | A list of words that mean something moral |
| **Syntax** | Grammar - how words are arranged in a sentence |
| **Negation** | Words like "not", "never", "no" that flip the meaning |
| **Score** | How much the app thinks the sentence is about morals |

## Tech Stack

- Python
- spaCy (NLP)
- scikit-learn (Machine Learning)
- Streamlit (Frontend)
- TF-IDF with syntactic features