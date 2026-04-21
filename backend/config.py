"""
Configuration Settings for Syntactic Morality Analyzer

Based on professors' research:
- Malik et al. (2025) eMACD
- Hopp et al. (2021) eMFD
- Graham et al. (2013) MFD 2.0
- Curry et al. (2019) MACD
"""

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# spaCy Settings
SPACY_MODEL = "en_core_web_sm"  # Small model - faster

# Dictionary files
DICTIONARIES = {
    "mfd": "mfd.json",
    "mfd2": "mfd2.json",
    "emfd": "emfd.json",
    "emacd": "emacd.json",
    "macd": "macd.json"
}

# Moral Foundations Theory domains (MFT)
LABELS_MFT = [
    "Care",
    "Equality", 
    "Proportionality",
    "Authority",
    "Loyalty",
    "Purity"
]

# Morality as Cooperation domains (MAC)
LABELS_MAC = [
    "Family",
    "Group Loyalty",
    "Reciprocity",
    "Heroism",
    "Deference",
    "Fairness",
    "Property Rights"
]

# Classification Settings
TFIDF_MAX_FEATURES = 200
TFIDF_NGRAM_RANGE = (1, 2)

# Model Settings
LOGISTIC_REGRESSION_C = 0.1  # Regularization
MAX_ITERATIONS = 500

# Feature weights for syntactic analysis
ROLE_WEIGHTS = {
    "nsubj": 1.5,       # Grammatical subject: boost
    "nsubjpass": 1.5,   # Passive subject
    "dobj": 1.3,        # Direct object: slight boost
    "pobj": 1.2,        # Prepositional object
    "ROOT": 1.2,        # Main verb
    "amod": 0.8,        # Adjectival modifier: reduce
    "advmod": 0.8,      # Adverbial modifier: reduce
    "neg": 0.0          # Negation: zero out
}

# Negation tokens
NEGATION_TOKENS = {"not", "n't", "never", "no", "neither", "nor", "none", "nothing"}

# Dependency roles for moral analysis
SUBJ_ROLES = {"nsubj", "nsubjpass"}
OBJ_ROLES = {"dobj", "pobj", "iobj"}
MOD_ROLES = {"amod", "advmod", "neg"}
VERB_ROLES = {"ROOT", "conj", "cc"}

# Application info
APP_NAME = "Syntactic Morality Analyzer"
APP_TAGLINE = "Extension to eMACDscore with syntactic analysis"
APP_VERSION = "1.0.0"