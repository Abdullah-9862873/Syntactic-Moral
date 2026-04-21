"""
Module 5: Feature Extraction

Extracts features for Logistic Regression classifier:
- TF-IDF features
- Syntactic features
- Combined features

Based on Course 04 (Neural Networks & PyTorch) concepts.
"""

import numpy as np
from typing import List, Dict
import sys
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix, hstack

# Dynamic import for parser
_pipeline_dir = Path(__file__).parent
if str(_pipeline_dir) not in sys.path:
    sys.path.insert(0, str(_pipeline_dir))

from syntactic_parser import SyntacticParser


class FeatureExtractor:
    """
    Extract features for moral classification.
    
    Feature types:
    1. TF-IDF (bag-of-words)
    2. Syntactic (dependency-based)
    3. Combined
    """
    
    # Number of syntactic features per domain
    FEATURES_PER_DOMAIN = 4
    GENERAL_SYNTAX_FEATURES = 8
    
    def __init__(self, labels: List[str], parser: SyntacticParser):
        """
        Initialize feature extractor.
        
        Args:
            labels: List of domain labels
            parser: SyntacticParser instance
        """
        self.labels = labels
        self.parser = parser
        self.tfidf = None
    
    def fit_tfidf(self, texts: List[str]):
        """
        Fit TF-IDF vectorizer on training texts.
        
        Args:
            texts: List of training texts
        """
        self.tfidf = TfidfVectorizer(
            max_features=200,
            ngram_range=(1, 2),
            min_df=5,
            max_df=0.85
        )
        self.tfidf.fit(texts)
    
    def extract_tfidf(self, texts: List[str]) -> csr_matrix:
        """
        Extract TF-IDF features.
        
        Args:
            texts: List of texts
            
        Returns:
            Sparse matrix of TF-IDF features
        """
        if self.tfidf is None:
            raise ValueError("Call fit_tfidf() first")
        return self.tfidf.transform(texts)
    
    def extract_syntactic(self, texts: List[str], lexicons: dict) -> np.ndarray:
        """
        Extract syntactic features.
        
        Features per domain:
        - Word count (matches domain words)
        - Subject count (matches in subject position)
        - Object count (matches in object position)
        - Modifier count (matches as modifiers)
        
        Args:
            texts: List of texts
            lexicons: Dict mapping domain -> list of words
            
        Returns:
            (n_samples, n_features) array
        """
        features = []
        
        for text in texts:
            syntactic = self.parser.parse(text)
            fv = []
            
            # Features per domain
            for domain in self.labels:
                domain_words = lexicons.get(domain, [])
                
                # Get tokens in each role that match domain words
                kw_matches = [
                    t for t in syntactic["tokens"]
                    if any(kw in t.lower() for kw in domain_words)
                ]
                
                # Total keyword count
                fv.append(len(kw_matches))
                
                # Subject count
                subj_texts = [s["text"] for s in syntactic["subjects"]]
                subj_matches = [t for t in kw_matches if t in subj_texts]
                fv.append(len(subj_matches))
                
                # Object count
                obj_texts = [s["text"] for s in syntactic["objects"]]
                obj_matches = [t for t in kw_matches if t in obj_texts]
                fv.append(len(obj_matches))
                
                # Modifier count
                mod_texts = [s["text"] for s in syntactic["modifiers"]]
                mod_matches = [t for t in kw_matches if t in mod_texts]
                fv.append(len(mod_matches))
            
            # General syntactic features
            # Total moral keywords in text
            all_kw = []
            for words in lexicons.values():
                all_kw.extend(words)
            fv.append(sum(1 for t in syntactic["tokens"] 
                       if any(kw in t.lower() for kw in all_kw)))
            
            # Dependency counts
            for dep in ["nsubj", "dobj", "ROOT", "prep", "amod", "advmod", "punct"]:
                fv.append(sum(1 for d in syntactic["dependencies"] if d == dep))
            
            # Sentence length
            fv.append(len(syntactic["tokens"]))
            
            features.append(fv)
        
        return np.array(features)
    
    def extract_combined(self, texts: List[str], lexicons: dict) -> csr_matrix:
        """
        Extract combined TF-IDF + syntactic features.
        
        Args:
            texts: List of texts
            lexicons: Dict mapping domain -> list of words
            
        Returns:
            Combined sparse feature matrix
        """
        tfidf = self.extract_tfidf(texts)
        syntactic = self.extract_syntactic(texts, lexicons)
        
        return hstack([tfidf, csr_matrix(syntactic)])
    
    def get_feature_names(self) -> List[str]:
        """Get names of syntactic features."""
        names = []
        for domain in self.labels:
            names.extend([
                f"{domain}_count",
                f"{domain}_subject",
                f"{domain}_object", 
                f"{domain}_modifier"
            ])
        names.extend([
            "total_keywords",
            "nsubj_count",
            "dobj_count", 
            "ROOT_count",
            "prep_count",
            "amod_count",
            "advmod_count",
            "punct_count",
            "sentence_length"
        ])
        return names


def extract_features(texts: List[str], labels: List[str], 
                  parser: SyntacticParser,
                  lexicons: dict,
                  fit: bool = True):
    """
    Quick feature extraction function.
    
    Args:
        texts: List of texts
        labels: Domain labels
        parser: SyntacticParser
        lexicons: Dictionary words per domain
        fit: Whether to fit TF-IDF (True for training)
        
    Returns:
        Combined feature matrix
    """
    extractor = FeatureExtractor(labels, parser)
    
    if fit:
        extractor.fit_tfidf(texts)
    
    return extractor.extract_combined(texts, lexicons)