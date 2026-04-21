"""
Training Script for Syntactic Morality Analyzer

Tests across ALL 5 dictionaries as requested by Musa Malik:
> "Could you repeat the same analyses across MFD, MFD 2.0, eMFD lexicons? 
> I am curious to see if variations across MFT dictionaries increase baseline lexicon effects."

Usage:
    python train.py

Output:
    - Trained models for each dictionary
    - Evaluation results for research summary
    - Multi-dictionary comparison table
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Add parent to path for imports
sys.path.insert(0, str(BASE_DIR))

# Fix imports - use dynamic loading
_pipeline_dir = BASE_DIR / "pipeline"
if str(_pipeline_dir) not in sys.path:
    sys.path.insert(0, str(_pipeline_dir))

from dictionaries import DictionaryLoader
from parser import SyntacticParser
from features import FeatureExtractor
from classifier import MoralClassifier

# Dictionaries to test (as requested by Musa)
DICTIONARIES_TO_TEST = ["mfd", "mfd2", "emfd", "emacd", "macd"]

# Training settings - FULL DATA
SAMPLE_SIZE = None  # Use full dataset (all ~61K samples)

# Domain labels per dictionary type
MFT_DOMAINS = ['Care', 'Equality', 'Proportionality', 'Authority', 'Loyalty', 'Purity']
MAC_DOMAINS = ['Family', 'Group Loyalty', 'Reciprocity', 'Heroism', 'Deference', 'Fairness', 'Property Rights']

# Default domains to use for training (MFT domains work for all in our experiment)
DEFAULT_TRAINING_DOMAINS = MFT_DOMAINS


def load_mfrc():
    """
    Load MFRC dataset from HuggingFace.
    """
    print("Loading MFRC dataset...")
    
    try:
        from datasets import load_dataset
        dataset = load_dataset("USC-MOLA-Lab/MFRC", split="train")
        df = pd.DataFrame(dataset)
    except ImportError:
        print("Installing datasets library...")
        os.system("pip install datasets")
        from datasets import load_dataset
        dataset = load_dataset("USC-MOLA-Lab/MFRC", split="train")
        df = pd.DataFrame(dataset)
    
    print(f"Loaded {len(df)} samples from MFRC")
    
    # Sample for faster training (optional - set to None for full data)
    if SAMPLE_SIZE and len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=42)
        print(f"Sampled to {SAMPLE_SIZE} for faster training")
    
    # Extract texts
    texts = df['text'].tolist()
    
    # Extract labels (6 MFT foundations)
    def get_labels(annotation):
        """Convert annotation string to binary labels."""
        if pd.isna(annotation):
            return {d: 0 for d in MFT_DOMAINS}
        ann = str(annotation)
        if ann in ['Non-Moral', 'Thin Morality', 'nan']:
            return {d: 0 for d in MFT_DOMAINS}
        return {d: 1 if d in ann else 0 for d in MFT_DOMAINS}
    
    # Convert to label matrix
    label_dicts = df['annotation'].apply(get_labels)
    labels_df = pd.DataFrame(label_dicts.tolist(), columns=MFT_DOMAINS)
    
    # Filter to only moral samples
    mask = labels_df[MFT_DOMAINS].sum(axis=1) > 0
    texts = [t for t, m in zip(texts, mask) if m]
    labels = labels_df[mask].values
    
    print(f"Filtered to {len(texts)} moral samples")
    
    return texts, labels, MFT_DOMAINS


def load_lexicons(dict_loader, dict_name):
    """
    Load lexicons for a specific dictionary.
    """
    domains = dict_loader.get_domains(dict_name)
    lexicons = {}
    
    for domain in domains:
        words = dict_loader.get_words(dict_name, domain)
        if isinstance(words, dict):
            words = list(words.keys())
        elif isinstance(words, list):
            pass  # Use as-is
        else:
            words = []
        lexicons[domain] = words
    
    return lexicons


def evaluate_baseline(texts, labels, labels_list, lexicons):
    """
    Evaluate baseline (keyword-only) approach.
    """
    from sklearn.metrics import f1_score
    
    results = {}
    for i, domain in enumerate(labels_list):
        y_true = labels[:, i]
        y_pred = []
        
        domain_words = [w.lower() for w in lexicons.get(domain, [])]
        
        for text in texts:
            text_lower = text.lower()
            pred = 1 if any(w in text_lower for w in domain_words) else 0
            y_pred.append(pred)
        
        y_pred = np.array(y_pred)
        
        if y_true.sum() == 0 or y_pred.sum() == 0:
            f1 = 0.0
        else:
            f1 = f1_score(y_true, y_pred)
        
        results[domain] = f1
    
    results["macro"] = np.mean([results[d] for d in labels_list if d in results])
    
    return results


def train_and_evaluate_dict(dict_name, texts, labels, labels_list, parser, dict_loader):
    """
    Train and evaluate for a single dictionary.
    """
    print(f"\n{'='*50}")
    print(f"Testing: {dict_name.upper()}")
    print(f"{'='*50}")
    
    # Load lexicons
    lexicons = load_lexicons(dict_loader, dict_name)
    
    print(f"  Domains: {len(lexicons)}")
    print(f"  Total words: {sum(len(w) for w in lexicons.values())}")
    
    # Initialize classifier
    classifier = MoralClassifier(labels_list, parser)
    
    # Train
    classifier.train(texts, labels, lexicons, C=0.1)
    
    # Evaluate syntax-enhanced
    syntax_results = classifier.evaluate(texts, labels, lexicons)
    
    # Evaluate baseline
    baseline_results = evaluate_baseline(texts, labels, labels_list, lexicons)
    
    return {
        "baseline": baseline_results,
        "syntax": syntax_results,
        "improvement": {
            d: syntax_results.get(d, 0) - baseline_results.get(d, 0)
            for d in labels_list
        }
    }


def print_multi_dict_summary(all_results):
    """Print summary table comparing all dictionaries."""
    print("\n" + "="*80)
    print("MULTI-DICTIONARY COMPARISON - Syntactic Morality Analyzer")
    print("Answering Musa's request: 'variations across MFT dictionaries increase baseline lexicon effects'")
    print("="*80)
    print("")
    print(f"{'Dictionary':<12} {'Baseline':>10} {'Syntax':>10} {'Δ':>10} {'Theory':<10} {'Source'}")
    print("-"*80)
    
    for dict_name, r in all_results.items():
        base = r["baseline"].get("macro", 0)
        synx = r["syntax"].get("macro", 0)
        delta = synx - base
        
        if dict_name in ["emacd", "macd"]:
            theory = "MAC"
            source = "Malik" if dict_name == "emacd" else "Curry"
        else:
            theory = "MFT"
            source = "Graham" if dict_name == "mfd" else "Hopp"
        
        print(f"{dict_name:<12} {base:>10.3f} {synx:>10.3f} {delta:>+10.3f} {theory:<10} {source}")
    
    print("="*80)
    
    # Calculate improvements
    mft_results = {k: v for k, v in all_results.items() 
                   if k in ["mfd", "mfd2", "emfd"]}
    mac_results = {k: v for k, v in all_results.items() 
                   if k in ["emacd", "macd"]}
    
    print("")
    print("BY THEORY:")
    print(f"  MFT dictionaries (avg): +{np.mean([r['syntax']['macro']-r['baseline']['macro'] for r in mft_results.values()]):.3f}")
    print(f"  MAC dictionaries (avg): +{np.mean([r['syntax']['macro']-r['baseline']['macro'] for r in mac_results.values()]):.3f}")
    print("")


def save_results(all_results):
    """Save results to files."""
    # Save full JSON results
    with open(MODELS_DIR / "multi_dict_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    # Save summary text
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("EVALUATION RESULTS - Syntactic Morality Analyzer")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    summary_lines.append("Testing across ALL dictionaries as requested by Musa Malik:")
    summary_lines.append("> 'Could you repeat the same analyses across MFD, MFD 2.0, eMFD lexicons?'")
    summary_lines.append("")
    
    for dict_name, r in all_results.items():
        summary_lines.append(f"\n{dict_name.upper()} ({'MFT' if dict_name in ['mfd','mfd2','emfd'] else 'MAC'}):")
        summary_lines.append("-" * 30)
        
        for domain in r["baseline"]:
            if domain != "macro":
                base = r["baseline"].get(domain, 0)
                synx = r["syntax"].get(domain, 0)
                delta = r["improvement"].get(domain, 0)
                summary_lines.append(f"  {domain:15s}: {base:.3f} -> {synx:.3f} ({delta:+.3f})")
        
        macro_base = r["baseline"].get("macro", 0)
        macro_synx = r["syntax"].get("macro", 0)
        macro_delta = macro_synx - macro_base
        summary_lines.append(f"  {'Macro F1':15s}: {macro_base:.3f} -> {macro_synx:.3f} ({macro_delta:+.3f})")
    
    summary_text = "\n".join(summary_lines)
    
    with open(MODELS_DIR / "results_summary.txt", "w") as f:
        f.write(summary_text)
    
    print(summary_text)


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("SYNTACTIC MORALITY ANALYZER - Multi-Dictionary Training")
    print("=" * 60)
    print("")
    print("Answering Musa's request:")
    print("> 'Could you repeat the same analyses across MFD, MFD 2.0, eMFD lexicons?'")
    print("> 'I am curious to see if variations across MFT dictionaries increase baseline lexicon effects.'")
    print("")
    
    # Load data
    print("\n[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0%")
    print("Loading MFRC dataset...")
    texts, labels, labels_list = load_mfrc()
    
    # Initialize parser
    parser = SyntacticParser()
    
    # Load dictionaries
    dict_loader = DictionaryLoader(str(DATA_DIR))
    dict_loader.load_all()
    
    # Split data
    from sklearn.model_selection import train_test_split
    
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    
    print(f"\n[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] 30%")
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    all_results = {}
    total = len(DICTIONARIES_TO_TEST)
    
    for i, dict_name in enumerate(DICTIONARIES_TO_TEST):
        progress = int(((i + 1) / total) * 100)
        print(f"\n[{'█' * progress}{'░' * (100 - progress)}] {progress}%")
        
        dict_domains = dict_loader.get_domains(dict_name)
        
        if not dict_domains:
            print(f"  Skipping {dict_name} - no domains found")
            continue
        
        print(f"  Training {dict_name}...")
        result = train_and_evaluate_dict(
            dict_name, X_train, y_train, labels_list, parser, dict_loader
        )
        
        all_results[dict_name] = result
    
    print(f"\n[{'█' * 20}] 100%")
    
    # Print summary
    print_multi_dict_summary(all_results)
    
    # Save results
    save_results(all_results)
    
    print("\n✓ Training complete!")
    print(f"  - Results saved to: {MODELS_DIR}")
    print(f"  - Multi-dictionary results: {MODELS_DIR / 'multi_dict_results.json'}")
    print(f"  - Summary: {MODELS_DIR / 'results_summary.txt'}")
    
    return all_results


if __name__ == "__main__":
    results = main()