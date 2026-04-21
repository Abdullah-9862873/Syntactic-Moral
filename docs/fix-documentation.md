# Bug Fixes and Improvements

## Date: April 21, 2026

## Issues Identified and Fixed

### Issue 1: Negation Not Working Properly

**Problem:**
When users entered sentences with negation like "We can never be good friends", the system did not show any moral bars (emotions). The negation was not being properly detected.

**Root Cause:**
The negation scoping logic in `syntactic_parser.py` only captured tokens in the head verb's subtree. For adverbial negations like "never" modifying linking verbs (be, seem, become), the predicate nominative (the noun "friends") was not included in the negation scope.

**Datasets Tested:**
- MFD (Moral Foundations Dictionary)
- eMFD (Extended Moral Foundations Dictionary)
- eMACD (Enhanced Moral And Cultural Dictionary)

**Fix Applied:**
Modified `_find_negation_scopes()` in `backend/pipeline/syntactic_parser.py` to:
1. Include all tokens in the negation's own subtree
2. Include all tokens from the head verb's subtree
3. For copular/linking verbs (be, seem, become, remain, stay), also capture predicate nominatives and complements (attr, acomp, pcomp, nsubj dependencies)

**Result:**
- "We can never be good friends" → Correctly shows 0.0 loyalty (negated)
- "We are good friends" → Correctly shows positive loyalty

---

### Issue 2: "friend" Not in Dictionary

**Problem:**
Sentences containing "friend" or related words (ally, companion, etc.) were not being detected for the Loyalty domain.

**Root Cause:**
The emacd.json dictionary did not include words like "friend", "ally", "companion" under the "Group Loyalty" domain.

**Datasets Used:**
- MFD (Moral Foundations Dictionary) - had "friend" under Loyalty
- eMACD (Enhanced Moral And Cultural Dictionary) - was missing these words

**Fix Applied:**
Added the following words to `Group Loyalty` in `backend/data/emacd.json`:
- friend: 0.75
- friends: 0.75
- ally: 0.72
- allies: 0.72
- companion: 0.70
- partnership: 0.68
- bond: 0.65

---

### Issue 3: Overly Aggressive Substring Matching

**Problem:**
Sentences like "I am very frustrated because I got you as my ally" showed unexpectedly high loyalty scores. The word "ally" should not have matched "loyalty" related words.

**Root Cause:**
The matching logic in `scorer.py` used bidirectional substring matching:
```python
if word in token_lower or token_lower in word:
```
This caused false positives where partial matches would incorrectly trigger (e.g., "ally" matching nothing, but causing confusion in the matching logic).

**Fix Applied:**
Changed to exact matching only in `backend/pipeline/scorer.py`:
```python
if word_clean == token_text_clean:
    matched_word = word_clean
```

Additionally, added lemmatization support to match word roots:
```python
# Also check lemma matching if no exact match found
if not matched_word and idx < len(syntactic["lemmas"]):
    lemma = syntactic["lemmas"][idx].lower().strip()
    for word in domain_words:
        word_clean = word.strip()
        if word_clean == lemma:
            matched_word = word_clean
            break
```

**Result:**
- "I got you as my ally" → Loyalty: 0.144 (was incorrectly high before)
- "ally" alone → Loyalty: 0.864 (correct, since ally is now in dictionary)

---

## Summary of Changes

| File | Change |
|------|--------|
| `backend/data/emacd.json` | Added friend, ally, companion, partnership, bond to Group Loyalty |
| `backend/pipeline/syntactic_parser.py` | Enhanced negation scoping to handle copular verbs |
| `backend/pipeline/scorer.py` | Fixed substring matching to exact match, added lemma support |

---

## Test Results

| Input | Before Fix | After Fix |
|-------|------------|-----------|
| "We can never be good friends" | 0.0 (no detection) | 0.0 Group Loyalty (negated correctly) |
| "We are good friends" | 0.0 | 0.1875 Group Loyalty |
| "I got you as my ally" | High (incorrect) | 0.144 Group Loyalty |
| "ally" | No match | 0.864 Group Loyalty |

---

### Issue 4: Negation Shows No Bars

**Problem:**
Sentences with negation like "I am not caring about fairness" showed NO bars at all in MFD, eMFD, eMACD. User expected to see bars (even if low) to know which moral words were detected.

**Root Cause:**
1. The word "caring" and "fairness" were not in dictionaries (only "care" and "fair")
2. When negation was detected, the weight was set to 0.0, making the score zero

**Datasets Used:**
- MFD (Moral Foundations Dictionary)
- eMFD (Extended Moral Foundations Dictionary)
- eMACD (Enhanced Moral And Cultural Dictionary)

**Fix Applied:**

1. Added word variations to dictionaries:
   
   **MFD:**
   - Care: caring, cared, cares, protecting, loving
   - Equality: fairness, fairly, fairer, equal, equality, just
   
   **eMFD:**
   - Care: caring (0.80), cared (0.78), caring (0.80), protecting (0.78)
   - Equality: fairness (0.80), fairly (0.78), fairer (0.76), equality (0.78)
   
   **eMACD:**
   - Family: caring (0.72), loved (0.68), loving (0.65)
   - Fairness: fairness (0.82), fairly (0.80), equality (0.80)

2. Changed negation handling in `backend/pipeline/scorer.py`:
   - Instead of setting weight to 0.0 (zero), now use 0.3 (reduced but visible)
   - User should always see a bar to know which moral terms were detected

**Result:**
| Input | Result |
|-------|--------|
| "I am not caring about fairness" | Care: 0.05, Equality: 0.05 (visible bars) |
| "I care about fairness" | Care: 0.3, Equality: 0.3 (positive bars) |

---

## Summary of All Changes

| File | Change |
|------|--------|
| `backend/data/mfd.json` | Added caring, fairness, equality, loving + variations |
| `backend/data/emfd.json` | Added caring, fairness, equality, loving + variations |
| `backend/data/emacd.json` | Added friend, ally, caring, fairness, equality + variations |
| `backend/pipeline/syntactic_parser.py` | Enhanced negation scoping |
| `backend/pipeline/scorer.py` | Fixed exact matching + lemma support + reduced negation weight (0.3 instead of 0.0) |
| `backend/tests/test_moral_scoring.py` | Added automated test suite |

---

## Automated Test Results

Run tests with: `python backend/tests/test_moral_scoring.py`

**Current Status: 13/13 PASSING**

| Test | Sentence | Expected | Result |
|------|----------|----------|--------|
| Negation 1 | "I am not caring about fairness" | Care, Equality > 0 | PASS |
| Negation 2 | "We can never be good friends" | Loyalty > 0 | PASS |
| Correlative | "not only...but" | Full scores | PASS |
| Positive 1 | "I care about my family" | Care, Loyalty > 0 | PASS |
| Positive 2 | "We are good friends" | Loyalty > 0 | PASS |
| Positive 3 | "I love my brother and sister" | Care, Loyalty > 0 | PASS |
| Positive 4 | "fairness and justice" | Equality > 0 | PASS |
| Family 1 | "my mother and father" | Care, Loyalty > 0 | PASS |
| Family 2 | "my son and daughter" | Care, Loyalty > 0 | PASS |
| Trust | "I trust you with my heart" | Care > 0 | PASS |
| Close | "we are close friends" | Care, Loyalty > 0 | PASS |
| Ally | "you are my ally" | Loyalty > 0 | PASS |
| Companion | "I got you as my companion" | Loyalty > 0 | PASS |

---

### Issue 5: "not only...but" False Negation + Missing Words

**Problem:**
Sentence "You are not only my friend but my brother by heart" showed:
- Incorrectly treated "not" as negation, reducing ALL scores
- Loyalty only at 0.027 (too low)
- Missing Care/Family domain (not detecting brother, heart)

**Root Cause:**
1. "not only...but" is correlative conjunction (meaning "both"), NOT negation - parser incorrectly negated everything
2. Words like "brother", "heart", "sister", "trust", "kindness" not in dictionaries

**Datasets Used:**
- MFD (Moral Foundations Dictionary)
- eMFD (Extended Moral Foundations Dictionary)
- eMACD (Enhanced Moral And Cultural Dictionary)

**Fix Applied:**

1. Added correlative negation detection in `syntactic_parser.py`:
   - Pattern "not only...but" now only affects "not" token itself
   - Other moral words get full score

2. Added words to dictionaries:
   
   **All dictionaries:**
   - brother, sister, heart, trust, family, kin, relative
   - kindness, caring, loving, close, intimate, faithful

**Result:**
| Input | Before | After |
|-------|--------|-------|
| "not only my friend but my brother" | Loyalty: 0.027 | Care: 0.2, Loyalty: 0.18 (MFD) |
| | | Family: 0.14, Group Loyalty: 0.21 (eMACD) |

---

## Complete Summary

| File | Changes |
|------|--------|
| `backend/data/mfd.json` | +brother, sister, heart, trust, family, kindness + variations |
| `backend/data/emfd.json` | +brother, sister, heart, trust, family, kindness + variations |
| `backend/data/emacd.json` | +brother, sister, heart, trust, friend, ally + variations |
| `backend/pipeline/syntactic_parser.py` | Fixed "not only...but" false negation |
| `backend/pipeline/scorer.py` | Exact matching + lemma + negation weight 0.3 |
