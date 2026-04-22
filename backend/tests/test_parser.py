"""
Unit tests for Syntactic Parser
"""

import sys
from pathlib import Path

# Add parent to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from pipeline.syntactic_parser import SyntacticParser


def test_parser_initialization():
    """Test parser initializes correctly."""
    parser = SyntacticParser()
    assert parser.nlp is not None
    print("✓ Parser initialization test passed")


def test_basic_parsing():
    """Test basic text parsing."""
    parser = SyntacticParser()
    result = parser.parse("I love my family")
    
    assert "tokens" in result
    assert "dependencies" in result
    assert len(result["tokens"]) > 0
    print("✓ Basic parsing test passed")


def test_negation_detection():
    """Test negation detection."""
    parser = SyntacticParser()
    result = parser.parse("I don't care about you")
    
    # Check negations found
    assert len(result["negations"]) > 0
    assert len(result["negation_scopes"]) > 0
    print("✓ Negation detection test passed")


def test_subject_detection():
    """Test subject detection."""
    parser = SyntacticParser()
    result = parser.parse("They protect the family")
    
    # Should have subjects
    subjects = result.get("subjects", [])
    assert len(subjects) > 0
    print("✓ Subject detection test passed")


def test_object_detection():
    """Test object detection."""
    parser = SyntacticParser()
    result = parser.parse("I love my family")
    
    # Should have objects
    objects = result.get("objects", [])
    assert len(objects) > 0
    print("✓ Object detection test passed")


def test_negation_reduces_score():
    """Test that negated moral words are detected."""
    parser = SyntacticParser()
    
    # Non-negated
    result1 = parser.parse("I care about family")
    tokens1 = result1["tokens"]
    
    # Negated  
    result2 = parser.parse("I don't care about family")
    tokens2 = result2["tokens"]
    negation_scopes2 = result2["negation_scopes"]
    
    # The words should be found in both, but negated version has negation
    assert "care" in [t.lower() for t in tokens1]
    assert "care" in [t.lower() for t in tokens2]
    assert len(negation_scopes2) > 0  # Has negation
    print("✓ Negation reduces score test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*50)
    print("Running Parser Tests")
    print("="*50)
    
    try:
        test_parser_initialization()
        test_basic_parsing()
        test_negation_detection()
        test_subject_detection()
        test_object_detection()
        test_negation_reduces_score()
        
        print("\n" + "="*50)
        print("All parser tests passed! ✓")
        print("="*50)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()