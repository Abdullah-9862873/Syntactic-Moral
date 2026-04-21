"""
Module 3: Syntactic Parser using spaCy

Extracts syntactic features from text using dependency parsing.

Features extracted:
- Grammatical roles (subject, object, modifier)
- Negation scope detection
- Subject-object relationships
- Dependency tree structure

Based on spaCy dependency parsing.

Usage:
    from pipeline.parser import SyntacticParser
    parser = SyntacticParser()
    features = parser.parse("I love my family")
"""

import spacy
import subprocess
from typing import Dict, List, Tuple, Optional

# Simple default config - avoid complex loading
DEFAULT_SPACY_MODEL = "en_core_web_sm"


class SyntacticParser:
    """
    Extract syntactic features from text using spaCy dependency parsing.
    
    This parser adds syntactic awareness to moral dictionary matching:
    - Detects who is the subject (moral agent)
    - Detects who is the object (moral patient)
    - Detects negation scope ("not caring" vs "caring")
    - Adds weighting based on grammatical role
    """
    
    # Dependency roles for moral analysis
    SUBJ_ROLES = {"nsubj", "nsubjpass"}      # Grammatical subject
    OBJ_ROLES = {"dobj", "pobj", "iobj"}     # Object (direct, prepositional, indirect)
    MOD_ROLES = {"amod", "advmod", "neg"}    # Modifiers (adjectival, adverbial, negation)
    VERB_ROLES = {"ROOT", "conj", "cc"}        # Verbs
    
    # Negation tokens
    NEG_TOKENS = {"not", "n't", "never", "no", "neither", "nor", "none", "nothing", "nobody"}
    
    def __init__(self, model_name: str = None):
        """
        Initialize spaCy model.
        
        Args:
            model_name: Name of spaCy model (default: en_core_web_md from config)
        """
        self.model_name = model_name or DEFAULT_SPACY_MODEL
        self.nlp = self._load_model()
    
    def _load_model(self):
        """
        Load spaCy model, downloading if necessary.
        
        Returns:
            Loaded spaCy model
        """
        try:
            return spacy.load(self.model_name)
        except OSError:
            print(f"Downloading spaCy model: {self.model_name}...")
            subprocess.run(
                ["python", "-m", "spacy", "download", self.model_name],
                capture_output=True
            )
            return spacy.load(self.model_name)
    
    def parse(self, text: str) -> Dict:
        """
        Parse text and extract syntactic features.
        
        Args:
            text: Input text to parse
            
        Returns:
            Dictionary containing:
            - tokens: list of tokens
            - dependencies: dependency tags
            - heads: head relationships  
            - pos: part-of-speech tags
            - lemmas: lemmas
            - negations: negation tokens found
            - negation_scopes: tokens affected by each negation
            - subjects: subject tokens with info
            - objects: object tokens with info
            - modifiers: modifier tokens with info
            - verbs: verb tokens with info
        """
        doc = self.nlp(text)
        
        features = {
            "tokens": [],
            "dependencies": [],
            "heads": [],
            "pos": [],
            "lemmas": [],
            "negations": [],
            "negation_scopes": {},
            "subjects": [],
            "objects": [],
            "modifiers": [],
            "verbs": []
        }
        
        # Find negation scopes (tokens affected by each negation)
        negation_scopes = self._find_negation_scopes(doc)
        features["negation_scopes"] = negation_scopes
        
        for idx, token in enumerate(doc):
            # Basic token info
            features["tokens"].append(token.text)
            features["dependencies"].append(token.dep_)
            features["pos"].append(token.pos_)
            features["lemmas"].append(token.lemma_)
            
            # Head relationship
            features["heads"].append({
                "token": token.head.text,
                "relation": token.head.dep_
            })
            
            # Subject detection
            if token.dep_ in self.SUBJ_ROLES:
                features["subjects"].append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "dep": token.dep_,
                    "negated": idx in negation_scopes
                })
            
            # Object detection
            if token.dep_ in self.OBJ_ROLES:
                features["objects"].append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "dep": token.dep_,
                    "negated": idx in negation_scopes
                })
            
            # Modifier detection
            if token.dep_ in self.MOD_ROLES:
                features["modifiers"].append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "type": token.dep_,
                    "negated": idx in negation_scopes
                })
            
            # Verb detection
            if token.pos_ == "VERB" or token.dep_ in self.VERB_ROLES:
                features["verbs"].append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "negated": idx in negation_scopes
                })
            
            # Negation token
            if token.text.lower() in self.NEG_TOKENS or token.dep_ == "neg":
                features["negations"].append({
                    "text": token.text,
                    "index": idx,
                    "scope": negation_scopes.get(idx, [])
                })
        
        return features
    
    def _find_negation_scopes(self, doc) -> Dict[int, List[int]]:
        """
        Find negation tokens and their scope (tokens they modify).
        
        This is key for moral analysis:
        "not caring" should score differently than "caring"
        
        Returns:
            Dictionary mapping negation token index -> list of affected token indices
        """
        scopes = {}
        
        # Get token texts for context checking
        token_texts = [t.text.lower() for t in doc]
        
        for token in doc:
            if token.text.lower() in self.NEG_TOKENS or token.dep_ == "neg":
                # Check if this is "not only...but" correlative (not actual negation)
                # Pattern: "not only X but also Y" means BOTH/AND, not negation
                is_correlative = False
                if token.text.lower() == "not":
                    # Check if followed by "only" 
                    if token.i + 1 < len(doc) and doc[token.i + 1].text.lower() == "only":
                        is_correlative = True
                    # Also check if preceded by "not" and followed by "but" pattern
                    # "not only...but also" is correlative
                
                if is_correlative:
                    # For correlative "not only...but", only negate the "not" itself, not the rest
                    # This way it doesn't affect other moral words
                    scope = [token.i]
                    scopes[token.i] = scope
                    continue
                
                scope = [token.i]
                
                # Get all tokens in the negation's subtree
                for child in token.subtree:
                    scope.append(child.i)
                
                # Also traverse from the negation's head (the verb it modifies)
                # and get all tokens downstream from that verb
                head = token.head
                for t in head.subtree:
                    scope.append(t.i)
                
                # For copular/linking verbs (be, seem, become, etc.)
                # also get their complements (predicate nominatives)
                if head.lemma_ in {"be", "seem", "become", "remain", "stay"}:
                    for child in head.children:
                        if child.dep_ in {"attr", "acomp", "pcomp", "nsubj"}:
                            for t in child.subtree:
                                scope.append(t.i)
                        # Also include the child itself
                        scope.append(child.i)
                
                scopes[token.i] = list(set(scope))
        
        return scopes
    
    def is_negated(self, token_idx: int, negation_scopes: Dict) -> bool:
        """
        Check if a token is within negation scope.
        
        Args:
            token_idx: Token index to check
            negation_scopes: Dict of negation scopes
            
        Returns:
            True if token is negated
        """
        for neg_idx, scope in negation_scopes.items():
            if token_idx in scope:
                return True
        return False
    
    def get_grammatical_role(self, token: str, syntactic: Dict) -> str:
        """
        Get the grammatical role of a token.
        
        Args:
            token: Token text
            syntactic: Parsed features from parse()
            
        Returns:
            Dependency label (e.g., 'nsubj', 'dobj', 'amod')
        """
        for idx, t in enumerate(syntactic["tokens"]):
            if t == token:
                return syntactic["dependencies"][idx]
        return "unknown"
    
    def get_moral_relations(self, text: str) -> List[Dict]:
        """
        Extract subject-verb-object moral relations.
        
        Useful for understanding who is doing what to whom.
        
        Returns:
            List of {
                "agent": subject token,
                "action": verb,
                "patient": object token
            }
        """
        doc = self.nlp(text)
        relations = []
        
        for token in doc:
            if token.dep_ in self.SUBJ_ROLES:
                # Find associated action (verb)
                action = None
                for child in token.head.children:
                    if child.pos_ == "VERB":
                        action = child.text
                        break
                
                # If subject is head of clause, look at its children
                if token.head == token:  # subject is ROOT
                    for child in token.children:
                        if child.pos_ == "VERB":
                            action = child.text
                            break
                
                # Find patient (object)
                patient = None
                for child in token.head.children:
                    if child.dep_ in self.OBJ_ROLES:
                        patient = child.text
                        break
                
                if action and patient:
                    relations.append({
                        "agent": token.text,
                        "action": action,
                        "patient": patient
                    })
        
        return relations
    
    def get_sentence_structure(self, text: str) -> Dict:
        """
        Get simplified sentence structure.
        
        Returns:
            Dictionary with simplified structure:
            - subject: main subject
            - verb: main verb  
            - object: main object (if exists)
            - modifiers: list of modifiers
        """
        doc = self.nlp(text)
        
        subject = None
        verb = None
        obj = None
        modifiers = []
        
        for token in doc:
            if token.dep_ == "nsubj":
                subject = token.text
            elif token.dep_ == "ROOT":
                verb = token.text
            elif token.dep_ in self.OBJ_ROLES:
                obj = token.text
            elif token.dep_ in self.MOD_ROLES:
                modifiers.append(token.text)
        
        return {
            "subject": subject,
            "verb": verb,
            "object": obj,
            "modifiers": modifiers
        }


# Convenience function for quick parsing
def parse_text(text: str, model: str = None) -> Dict:
    """
    Parse text and extract syntactic features.
    
    Args:
        text: Input text
        model: Optional spaCy model name
        
    Returns:
        Syntactic features dictionary
    """
    parser = SyntacticParser(model)
    return parser.parse(text)


def is_negated_word(word: str, text: str, model: str = None) -> bool:
    """
    Check if a word is negated in the text.
    
    Args:
        word: Word to check
        text: Full text
        model: Optional spaCy model name
        
    Returns:
        True if word is negated
    """
    parser = SyntacticParser(model)
    features = parser.parse(text)
    
    # Find word index
    word_idx = None
    for idx, token in enumerate(features["tokens"]):
        if token.lower() == word.lower():
            word_idx = idx
            break
    
    if word_idx is None:
        return False
    
    return features["negation_scopes"] and word_idx in [
        scope for scopes in features["negation_scopes"].values() 
        for scope in scopes
    ]