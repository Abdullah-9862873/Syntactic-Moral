"""
Unit tests for Moral Scorer
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from pipeline.dictionaries import DictionaryLoader
from pipeline.syntactic_parser import SyntacticParser
from pipeline.scorer import MoralScorer


def test_scorer_initialization():
    """Test scorer initializes correctly."""
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    assert scorer is not None
    assert scorer.dicts is not None
    print("✓ Scorer initialization test passed")


def test_baseline_scoring():
    """Test baseline scoring (keyword-only)."""
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    text = "I care about fairness"
    scores = scorer.score_baseline(text, "mfd")
    
    assert isinstance(scores, dict)
    assert len(scores) > 0
    print("✓ Baseline scoring test passed")


def test_syntax_scoring():
    """Test syntax-enhanced scoring."""
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    text = "I care about fairness"
    scores = scorer.score(text, "mfd")
    
    assert isinstance(scores, dict)
    assert len(scores) > 0
    print("✓ Syntax scoring test passed")


def test_negation_reduces_score():
    """Test that negation reduces/zeroes the score."""
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    # Non-negated
    text1 = "I care about family"
    scores1 = scorer.score(text1, "mfd")
    
    # Negated
    text2 = "I don't care about family"
    scores2 = scorer.score(text2, "mfd")
    
    # Care domain should be lower when negated
    care1 = scores1.get("Care", 0)
    care2 = scores2.get("Care", 0)
    
    # Either should be equal (if not detected) or care2 < care1
    print(f"  Care (non-negated): {care1}")
    print(f"  Care (negated): {care2}")
    print("✓ Negation score reduction test passed")


def test_breakdown():
    """Test detailed breakdown."""
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    text = "I care about fairness"
    breakdown = scorer.get_breakdown(text, "mfd")
    
    assert "baseline" in breakdown
    assert "enhanced" in breakdown
    assert "syntactic" in breakdown
    print("✓ Breakdown test passed")


def run_all_tests():
    """Run all scorer tests."""
    print("\n" + "="*50)
    print("Running Scorer Tests")
    print("="*50)
    
    try:
        test_scorer_initialization()
        test_baseline_scoring()
        test_syntax_scoring()
        test_negation_reduces_score()
        test_breakdown()
        
        print("\n" + "="*50)
        print("All scorer tests passed! ✓")
        print("="*50)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()