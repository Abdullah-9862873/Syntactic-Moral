"""
Module 6: Classification Models

Train and use Logistic Regression classifiers for moral domains.

Based on Course 04 (Neural Networks & PyTorch) concepts.
One classifier per domain (multi-label).
"""

from typing import Dict, List
import sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

# Dynamic imports for sibling modules
_pipeline_dir = Path(__file__).parent
if str(_pipeline_dir) not in sys.path:
    sys.path.insert(0, str(_pipeline_dir))

from features import FeatureExtractor
from parser import SyntacticParser


class MoralClassifier:
    """
    Train and use classifiers for moral domains.
    
    One Logistic Regression per domain (multi-label classification).
    """
    
    def __init__(self, labels: List[str], parser: SyntacticParser):
        """
        Initialize classifier.
        
        Args:
            labels: List of domain labels
            parser: SyntacticParser instance
        """
        self.labels = labels
        self.parser = parser
        self.feature_extractor = FeatureExtractor(labels, parser)
        self.classifiers: Dict[str, LogisticRegression] = {}
        self._trained = False
    
    def train(self, texts: List[str], labels: np.ndarray, 
             lexicons: dict, C: float = 0.1):
        """
        Train classifiers for each domain.
        
        Args:
            texts: Training texts
            labels: (n_samples, n_domains) binary labels
            lexicons: Dict mapping domain -> list of words
            C: Regularization parameter
        """
        # Fit TF-IDF on training data
        self.feature_extractor.fit_tfidf(texts)
        
        # Train one classifier per domain
        for i, domain in enumerate(self.labels):
            # Extract combined features
            X = self.feature_extractor.extract_combined(texts, lexicons)
            y = labels[:, i]
            
            # Skip if no positive samples
            if y.sum() == 0:
                continue
            
            # Train logistic regression
            clf = LogisticRegression(
                C=C,
                class_weight="balanced",
                max_iter=5000,
                solver="lbfgs",
                random_state=42
            )
            clf.fit(X.toarray(), y)
            self.classifiers[domain] = clf
        
        self._trained = True
    
    def predict(self, texts: List[str], lexicons: dict) -> np.ndarray:
        """
        Predict moral domain labels.
        
        Args:
            texts: Texts to predict
            lexicons: Dict mapping domain -> list of words
            
        Returns:
            (n_samples, n_domains) binary predictions
        """
        if not self._trained:
            raise ValueError("Call train() first")
        
        predictions = []
        for domain in self.labels:
            if domain not in self.classifiers:
                predictions.append(np.zeros(len(texts)))
                continue
            
            X = self.feature_extractor.extract_combined(texts, lexicons)
            pred = self.classifiers[domain].predict(X.toarray())
            predictions.append(pred)
        
        return np.column_stack(predictions)
    
    def predict_proba(self, texts: List[str], lexicons: dict) -> Dict[str, np.ndarray]:
        """
        Predict probabilities per domain.
        
        Args:
            texts: Texts to predict
            lexicons: Dict mapping domain -> list of words
            
        Returns:
            Dict mapping domain -> probability array
        """
        if not self._trained:
            raise ValueError("Call train() first")
        
        probas = {}
        for domain in self.labels:
            if domain not in self.classifiers:
                probas[domain] = np.zeros(len(texts))
                continue
            
            X = self.feature_extractor.extract_combined(texts, lexicons)
            proba = self.classifiers[domain].predict_proba(X.toarray())[:, 1]
            probas[domain] = proba
        
        return probas
    
    def evaluate(self, texts: List[str], labels: np.ndarray,
               lexicons: dict) -> Dict[str, float]:
        """
        Evaluate on test set.
        
        Args:
            texts: Test texts
            labels: True labels (n_samples, n_domains)
            lexicons: Dict mapping domain -> list of words
            
        Returns:
            Dict with per-domain F1 and macro F1
        """
        results = {}
        
        for i, domain in enumerate(self.labels):
            if domain not in self.classifiers:
                results[domain] = 0.0
                continue
            
            X = self.feature_extractor.extract_combined(texts, lexicons)
            y_true = labels[:, i]
            y_pred = self.classifiers[domain].predict(X.toarray())
            
            f1 = f1_score(y_true, y_pred)
            results[domain] = f1
        
        # Macro F1
        valid_f1s = [f for f in results.values() if f > 0]
        results["macro"] = np.mean(valid_f1s) if valid_f1s else 0.0
        
        return results
    
    def is_trained(self) -> bool:
        """Check if classifiers are trained."""
        return self._trained


def train_classifier(texts: List[str], labels: np.ndarray,
                labels_list: List[str], parser: SyntacticParser,
                lexicons: dict, C: float = 0.1) -> MoralClassifier:
    """
    Quick function to train classifier.
    
    Args:
        texts: Training texts
        labels: Binary labels
        labels_list: Domain labels
        parser: SyntacticParser
        lexicons: Dictionary words
        C: Regularization
        
    Returns:
        Trained MoralClassifier
    """
    classifier = MoralClassifier(labels_list, parser)
    classifier.train(texts, labels, lexicons, C)
    return classifier