"""
Module 4: Moral Scoring with Syntactic Weighting

Extends eMACDscore (Malik et al., 2025) with syntactic layer.

Key improvements:
- Boost keywords in subject/object roles
- Downweight keywords in negation scope
- Add role-specific weights

Usage:
    from pipeline.scorer import MoralScorer
    scorer = MoralScorer(dict_loader, parser)
    scores = scorer.score("I care about family", "emacd")
"""

from typing import Dict, List
import sys
from pathlib import Path

# Dynamically import sibling modules
_pipeline_dir = Path(__file__).parent
sys.path.insert(0, str(_pipeline_dir))

from dictionaries import DictionaryLoader
from syntactic_parser import SyntacticParser


class MoralScorer:
    """
    Calculate moral domain scores with syntactic weighting.
    
    Extends eMACDscore approach:
    1. Get baseline dictionary score (original behavior)
    2. Apply syntactic weights based on grammatical role
    3. Zero out keywords in negation scope
    """
    
    # Weight multipliers for grammatical roles
    ROLE_WEIGHTS = {
        "nsubj": 1.5,       # Gramm subject: boost (moral agent)
        "nsubjpass": 1.5,   # Passive subject
        "dobj": 1.3,        # Direct object: slight boost (moral patient)
        "pobj": 1.2,        # Prepositional object
        "ROOT": 1.2,        # Main verb
        "amod": 0.8,        # Adjectival modifier: reduce
        "advmod": 0.8,     # Adverbial modifier: reduce
        "neg": 0.0,        # Negation: zero out
        "conj": 1.0,       # Conjunction: neutral
        "cc": 1.0,         # Coordinating conjunction
    }
    
    def __init__(self, dict_loader: DictionaryLoader, parser: SyntacticParser):
        """
        Initialize moral scorer.
        
        Args:
            dict_loader: DictionaryLoader instance
            parser: SyntacticParser instance
        """
        self.dicts = dict_loader
        self.parser = parser
        
        # Ensure dictionaries are loaded
        if not dict_loader.is_loaded():
            dict_loader.load_all()
    
    def score(self, text: str, dict_name: str = "emacd") -> Dict[str, float]:
        """
        Score text for moral domains with syntax enhancement.
        
        Args:
            text: Input text
            dict_name: Which dictionary to use (mfd, emfd, emacd, etc.)
            
        Returns:
            Dict mapping domain -> score (0.0 to 1.0)
        """
        # Parse syntactic structure
        syntactic = self.parser.parse(text)
        
        # Get domains for dictionary
        domains = self.dicts.get_domains(dict_name)
        
        scores = {}
        for domain in domains:
            scores[domain] = self._score_domain(
                text, domain, dict_name, syntactic
            )
        
        return scores
    
    def _score_domain(self, text: str, domain: str, 
                   dict_name: str, syntactic: Dict) -> float:
        """Score single domain with syntax weighting."""
        total_score = 0.0
        text_lower = text.lower()
        
        # Get words for this domain
        domain_words = self.dicts.get_words(dict_name, domain)
        
        # Score each keyword occurrence
        for token_text in syntactic["tokens"]:
            token_lower = token_text.lower()
            
            # Check if token matches any domain word (partial match)
            matched_word = None
            for word in domain_words:
                if word in token_lower or token_lower in word:
                    matched_word = word
                    break
            
            if matched_word:
                # Find grammatical role
                role = self._get_token_role(token_text, syntactic)
                
                # Check if negated
                is_negated = self._is_token_negated(token_text, syntactic)
                
                # Calculate weight
                weight = self.ROLE_WEIGHTS.get(role, 1.0)
                
                # Apply negation (zero out negated moral language)
                if is_negated:
                    weight = 0.0
                
                # Get word score from dictionary
                word_score = self.dicts.get_score(dict_name, domain, matched_word)
                if word_score == 0.0:
                    word_score = 1.0  # Binary dict: presence = 1.0
                
                total_score += word_score * weight
        
        # Normalize by text length to prevent bias toward long text
        num_tokens = len(syntactic["tokens"])
        if num_tokens > 0:
            total_score /= num_tokens
        
        return total_score
    
    def _get_token_role(self, token: str, syntactic: Dict) -> str:
        """Get grammatical role of token."""
        for idx, t in enumerate(syntactic["tokens"]):
            if t == token:
                return syntactic["dependencies"][idx]
        return "unknown"
    
    def _is_token_negated(self, token: str, syntactic: Dict) -> bool:
        """Check if token is in negation scope."""
        # Check each negation scope
        neg_scopes = syntactic.get("negation_scopes", {})
        
        for neg_idx, scope in neg_scopes.items():
            for idx, t in enumerate(syntactic["tokens"]):
                if t == token and idx in scope:
                    return True
        
        return False
    
    def score_baseline(self, text: str, dict_name: str = "emacd") -> Dict[str, float]:
        """
        Baseline scoring - matches original eMACDscore behavior.
        
        This is the simple bag-of-words approach without syntax.
        Used for comparison.
        
        Args:
            text: Input text
            dict_name: Which dictionary to use
            
        Returns:
            Dict mapping domain -> score
        """
        domains = self.dicts.get_domains(dict_name)
        
        scores = {}
        text_lower = text.lower()
        
        for domain in domains:
            words = self.dicts.get_words(dict_name, domain)
            
            score = 0.0
            for word in words:
                if word in text_lower:
                    # Probabilistic: add word score; Binary: add 1.0
                    word_score = self.dicts.get_score(dict_name, domain, word)
                    if word_score == 0.0:
                        word_score = 1.0
                    score += word_score
            
            # Normalize
            if len(words) > 0:
                score /= len(words)
            
            scores[domain] = score
        
        return scores
    
    def get_breakdown(self, text: str, dict_name: str = "emacd") -> Dict:
        """
        Get detailed breakdown for visualization.
        
        Returns:
            {
                "baseline": {...},
                "enhanced": {...},
                "difference": {...},
                "syntactic": {...}
            }
        """
        syntactic = self.parser.parse(text)
        baseline = self.score_baseline(text, dict_name)
        enhanced = self.score(text, dict_name)
        
        # Calculate difference
        difference = {
            d: enhanced[d] - baseline[d] 
            for d in baseline
        }
        
        breakdown = {
            "baseline": baseline,
            "enhanced": enhanced,
            "difference": difference,
            "syntactic": syntactic
        }
        
        return breakdown
    
    def compare_scores(self, text: str, dict_name: str = "emacd") -> Dict:
        """
        Compare baseline vs enhanced scores.
        
        Args:
            text: Input text
            dict_name: Dictionary to use
            
        Returns:
            Dict with baseline, enhanced, and difference per domain
        """
        baseline = self.score_baseline(text, dict_name)
        enhanced = self.score(text, dict_name)
        
        results = {}
        for domain in baseline:
            results[domain] = {
                "baseline": baseline[domain],
                "enhanced": enhanced[domain],
                "difference": enhanced[domain] - baseline[domain]
            }
        
        return results
    
    def get_domains_detected(self, text: str, dict_name: str = "emacd", 
                       threshold: float = 0.1) -> List[str]:
        """
        Get list of domains detected above threshold.
        
        Args:
            text: Input text
            dict_name: Dictionary to use
            threshold: Minimum score to consider "detected"
            
        Returns:
            List of domain names
        """
        scores = self.score(text, dict_name)
        return [d for d, s in scores.items() if s >= threshold]


def score_text(text: str, dict_name: str = "emacd", 
            dict_loader: DictionaryLoader = None,
            parser: SyntacticParser = None) -> Dict[str, float]:
    """
    Quick function to score text.
    
    Args:
        text: Input text
        dict_name: Dictionary name
        dict_loader: Optional pre-loaded DictionaryLoader
        parser: Optional pre-loaded SyntacticParser
        
    Returns:
        Domain scores
    """
    from .dictionaries import DictionaryLoader
    
    if dict_loader is None:
        dict_loader = DictionaryLoader(config.DATA_DIR)
        dict_loader.load_all()
    
    if parser is None:
        parser = SyntacticParser()
    
    scorer = MoralScorer(dict_loader, parser)
    return scorer.score(text, dict_name)