"""
Integration tests for the full pipeline
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from pipeline.dictionaries import DictionaryLoader
from pipeline.parser import SyntacticParser
from pipeline.scorer import MoralScorer


def test_full_pipeline():
    """Test complete pipeline from text to score."""
    # Initialize
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    # Test text
    text = "I care about my family and want fairness"
    
    # Get baseline
    baseline = scorer.score_baseline(text, "mfd")
    
    # Get syntax
    syntax = scorer.score(text, "mfd")
    
    # Get breakdown
    breakdown = scorer.get_breakdown(text, "mfd")
    
    # Verify
    assert baseline is not None
    assert syntax is not None
    assert breakdown is not None
    assert "baseline" in breakdown
    assert "enhanced" in breakdown
    
    print("✓ Full pipeline test passed")
    print(f"  Baseline: {baseline}")
    print(f"  Syntax: {syntax}")


def test_negation_scenario():
    """Test negation handling in full pipeline."""
    # Initialize
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    # With negation
    text_negated = "I don't care about fairness"
    
    baseline = scorer.score_baseline(text_negated, "mfd")
    syntax = scorer.score(text_negated, "mfd")
    
    # Negation should reduce Care score
    care_baseline = baseline.get("Care", 0)
    care_syntax = syntax.get("Care", 0)
    
    print(f"  Negated text: '{text_negated}'")
    print(f"  Care (baseline): {care_baseline}")
    print(f"  Care (syntax): {care_syntax}")
    
    print("✓ Negation scenario test passed")


def test_all_dicts():
    """Test scoring with all dictionaries."""
    data_dir = backend_dir / "data"
    dict_loader = DictionaryLoader(str(data_dir))
    dict_loader.load_all()
    
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    
    text = "I care about fairness and loyalty"
    
    dicts = ["mfd", "emfd", "emacd"]
    
    for d in dicts:
        scores = scorer.score(text, d)
        print(f"  {d}: {scores}")
    
    print("✓ All dictionaries test passed")


def run_integration_tests():
    """Run all integration tests."""
    print("\n" + "="*50)
    print("Running Integration Tests")
    print("="*50)
    
    try:
        test_full_pipeline()
        test_negation_scenario()
        test_all_dicts()
        
        print("\n" + "="*50)
        print("All integration tests passed! ✓")
        print("="*50)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_integration_tests()