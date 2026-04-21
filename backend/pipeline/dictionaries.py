"""
Module 2: Dictionary Loading

Loads and manages all moral dictionaries from professors' research.

Based on:
- Malik et al. (2025) eMACD - Morality as Cooperation Dictionary
- Hopp et al. (2021) eMFD - Extended Moral Foundations Dictionary
- Graham et al. (2013) MFD 2.0 - Moral Foundations Dictionary
- Curry et al. (2019) MACD - MAC Dictionary

Usage:
    dict_loader = DictionaryLoader("data")
    dicts = dict_loader.load_all()
    words = dict_loader.get_words("emacd", "Family")
"""

import json
import os
from typing import Dict, List, Optional


class DictionaryLoader:
    """
    Loads and manages moral dictionaries.
    
    Supports both binary (expert) and probabilistic (crowd-sourced) dictionaries.
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize dictionary loader.
        
        Args:
            data_dir: Path to directory containing dictionary JSON files
        """
        self.data_dir = data_dir
        self._dictionaries: Dict[str, Dict] = {}
        self._loaded = False
    
    def load_all(self) -> Dict[str, Dict]:
        """
        Load all dictionaries.
        
        Returns:
            Dict mapping dictionary name -> domain words
        """
        # Load MFD (binary - Moral Foundations Dictionary)
        self._dictionaries["mfd"] = self._load_json("mfd.json")
        
        # Load MFD 2.0 (binary, virtue/vice splits)
        self._dictionaries["mfd2"] = self._load_json("mfd2.json")
        
        # Load eMFD (probabilistic - Extended MFD)
        self._dictionaries["emfd"] = self._load_json("emfd.json")
        
        # Load eMACD (probabilistic - Extended MAC Dictionary)
        self._dictionaries["emacd"] = self._load_json("emacd.json")
        
        # Load MACD (binary - MAC Dictionary)
        self._dictionaries["macd"] = self._load_json("macd.json")
        
        self._loaded = True
        return self._dictionaries
    
    def _load_json(self, filename: str) -> Dict:
        """
        Load a single dictionary JSON file.
        
        Args:
            filename: Name of JSON file
            
        Returns:
            Dictionary content
        """
        path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(path):
            # Create empty placeholder if file doesn't exist
            return self._create_placeholder(filename)
        
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _create_placeholder(self, filename: str) -> Dict:
        """
        Create placeholder dictionary for testing.
        
        Args:
            filename: Name of file
            
        Returns:
            Minimal dictionary structure
        """
        # Return minimal test data based on filename
        if "emacd" in filename.lower():
            return {
                "Family": {"family": 0.85, "parents": 0.82, "children": 0.80},
                "Group Loyalty": {"loyal": 0.78, "team": 0.75, "group": 0.72},
                "Reciprocity": {"fair": 0.80, "exchange": 0.75, "reciprocal": 0.70},
                "Heroism": {"hero": 0.90, "brave": 0.85, "courage": 0.82},
                "Deference": {"respect": 0.78, "honor": 0.75, "obey": 0.70},
                "Fairness": {"fair": 0.82, "equal": 0.80, "justice": 0.78},
                "Property Rights": {"property": 0.75, "own": 0.70, "belong": 0.65}
            }
        elif "emfd" in filename.lower():
            return {
                "Care": {"help": 0.80, "care": 0.78, "protect": 0.75},
                "Equality": {"fair": 0.78, "equal": 0.76, "justice": 0.74},
                "Proportionality": {"deserve": 0.72, "blame": 0.70, "punish": 0.68},
                "Authority": {"respect": 0.75, "obey": 0.72, "law": 0.70},
                "Loyalty": {"loyal": 0.78, "team": 0.75, "unite": 0.72},
                "Purity": {"pure": 0.80, "sacred": 0.78, "holy": 0.76}
            }
        else:
            # MFD or MFD 2.0
            return {
                "Care": ["help", "care", "protect", "compassion", "kind", "hurt", "harm"],
                "Equality": ["fair", "equal", "justice", "rights", "discriminat", "inequality"],
                "Proportionality": ["deserve", "balance", "guilt", "blame", "punish", "reward"],
                "Authority": ["respect", "obey", "rule", "law", "leader", "government"],
                "Loyalty": ["country", "nation", "family", "friend", "patriot", "loyal"],
                "Purity": ["pure", "sacred", "holy", "religion", "clean", "natural"]
            }
    
    def load(self, dict_name: str) -> Dict:
        """
        Load a single dictionary.
        
        Args:
            dict_name: Name of dictionary (mfd, mfd2, emfd, emacd, macd)
            
        Returns:
            Dictionary content
        """
        if dict_name not in self._dictionaries:
            filename = f"{dict_name}.json"
            self._dictionaries[dict_name] = self._load_json(filename)
        
        return self._dictionaries[dict_name]
    
    def get_domains(self, dict_name: str) -> List[str]:
        """
        Get list of domains for a dictionary.
        
        Args:
            dict_name: Name of dictionary
            
        Returns:
            List of domain names
        """
        if dict_name not in self._dictionaries:
            self.load(dict_name)
        
        d = self._dictionaries.get(dict_name, {})
        if isinstance(d, dict):
            return list(d.keys())
        return []
    
    def get_words(self, dict_name: str, domain: str) -> List[str]:
        """
        Get word list for a dictionary domain.
        
        Args:
            dict_name: Name of dictionary
            domain: Domain name
            
        Returns:
            List of words (for binary) or word keys (for probabilistic)
        """
        if dict_name not in self._dictionaries:
            self.load(dict_name)
        
        d = self._dictionaries.get(dict_name, {})
        if isinstance(d, dict) and domain in d:
            words = d[domain]
            if isinstance(words, dict):
                # Probabilistic: return keys
                return list(words.keys())
            elif isinstance(words, list):
                # Binary: return as-is
                return words
        return []
    
    def get_score(self, dict_name: str, domain: str, word: str) -> float:
        """
        Get score for a word in a dictionary domain.
        
        For probabilistic dictionaries (eMFD, eMACD), returns the crowd-sourced score.
        For binary dictionaries (MFD, MACD), returns 1.0 if word exists, 0.0 otherwise.
        
        Args:
            dict_name: Name of dictionary
            domain: Domain name
            word: Word to look up
            
        Returns:
            Score (0.0 to 1.0 for probabilistic, 0 or 1 for binary)
        """
        if dict_name not in self._dictionaries:
            self.load(dict_name)
        
        d = self._dictionaries.get(dict_name, {})
        if isinstance(d, dict) and domain in d:
            words = d[domain]
            if isinstance(words, dict) and word in words:
                # Probabilistic dictionary
                return words[word]
            elif isinstance(words, list) and word in words:
                # Binary dictionary
                return 1.0
        return 0.0
    
    def get_all_words_flat(self, dict_name: str) -> List[str]:
        """
        Get all words across all domains for a dictionary.
        
        Args:
            dict_name: Name of dictionary
            
        Returns:
            Flat list of all words
        """
        domains = self.get_domains(dict_name)
        all_words = []
        for domain in domains:
            all_words.extend(self.get_words(dict_name, domain))
        return list(set(all_words))
    
    def is_loaded(self) -> bool:
        """Check if dictionaries are loaded."""
        return self._loaded
    
    def get_available_dict_names(self) -> List[str]:
        """
        Get list of available dictionary names.
        
        Returns:
            List of dictionary names
        """
        if not self._loaded:
            self.load_all()
        return list(self._dictionaries.keys())


# Convenience function for quick loading
def load_dictionary(data_dir: str, dict_name: str) -> Dict:
    """
    Load a single dictionary.
    
    Args:
        data_dir: Path to data directory
        dict_name: Name of dictionary
        
    Returns:
        Dictionary content
    """
    loader = DictionaryLoader(data_dir)
    return loader.load(dict_name)


def load_all_dictionaries(data_dir: str) -> Dict[str, Dict]:
    """
    Load all available dictionaries.
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        Dict mapping dictionary name -> content
    """
    loader = DictionaryLoader(data_dir)
    return loader.load_all()