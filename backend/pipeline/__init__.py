"""
Syntactic Morality Analyzer - Pipeline Package

Extension to eMACDscore (Malik et al., 2025) with syntactic analysis
"""

__version__ = "1.0.0"
__author__ = "Based on Malik et al. (2025), Hopp et al. (2021)"

# Import after modules are defined
try:
    from .dictionaries import DictionaryLoader
    from .syntactic_parser import SyntacticParser
    from .scorer import MoralScorer
    from .features import FeatureExtractor
    from .classifier import MoralClassifier
    
    __all__ = [
        "DictionaryLoader",
        "SyntacticParser",
        "MoralScorer",
        "FeatureExtractor",
        "MoralClassifier"
    ]
except ImportError:
    __all__ = []