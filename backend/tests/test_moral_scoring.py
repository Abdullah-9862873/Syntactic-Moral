"""
Automated Test Suite for Moral Sentiment Analysis

Tests all dictionary models against known sentences to verify correct behavior.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.dictionaries import DictionaryLoader
from pipeline.syntactic_parser import SyntacticParser
from pipeline.scorer import MoralScorer


class MoralSentimentTester:
    """Automated tester for moral sentiment analysis."""
    
    # Domain name mapping across dictionaries
    DOMAIN_MAP = {
        'mfd': {
            'Care': 'Care',
            'Loyalty': 'Loyalty', 
            'Equality': 'Equality'
        },
        'emfd': {
            'Care': 'Care',
            'Loyalty': 'Loyalty',
            'Equality': 'Equality'
        },
        'emacd': {
            'Care': 'Family',  # eMACD uses Family instead of Care
            'Loyalty': 'Group Loyalty',  # eMACD uses Group Loyalty
            'Equality': 'Fairness'  # eMACD uses Fairness
        }
    }
    
    def __init__(self):
        self.dict_loader = DictionaryLoader('backend/data')
        self.dict_loader.load_all()
        self.parser = SyntacticParser()
        self.scorer = MoralScorer(self.dict_loader, self.parser)
        self.dicts = ['mfd', 'emfd', 'emacd']
        self.passed = 0
        self.failed = 0
    
    def test(self, sentence: str, expected: dict, description: str = "") -> dict:
        """
        Test a sentence against expected results.
        
        Args:
            sentence: Input sentence
            expected: Dict {domain: min_score} or {domain: (min, max)}
            description: Test description
            
        Returns:
            Test result with pass/fail
        """
        results = {}
        all_passed = True
        failures = []
        
        for dict_name in self.dicts:
            scores = self.scorer.score(sentence, dict_name)
            results[dict_name] = scores
            
            for domain, expected_val in expected.items():
                # Map domain name to actual dictionary domain
                actual_domain = self.DOMAIN_MAP.get(dict_name, {}).get(domain, domain)
                
                # Skip if domain not in this dict
                if actual_domain not in scores:
                    # Determine expected min from tuple or value
                    min_expected = expected_val[0] if isinstance(expected_val, tuple) else expected_val
                    if min_expected > 0:
                        all_passed = False
                        failures.append(f"{dict_name}: {domain} not found (expected > 0)")
                    continue
                
                actual = scores[actual_domain]
                
                # Handle range or single value
                if isinstance(expected_val, tuple):
                    min_val, max_val = expected_val
                    if min_val > 0 and actual < min_val:
                        all_passed = False
                        failures.append(f"{dict_name}.{domain} = {actual:.3f} (expected >= {min_val})")
                    elif max_val > 0 and actual > max_val:
                        all_passed = False
                        failures.append(f"{dict_name}.{domain} = {actual:.3f} (expected <= {max_val})")
                else:
                    if expected_val > 0 and actual <= 0:
                        all_passed = False
                        failures.append(f"{dict_name}.{domain} = {actual} (expected > 0)")
        
        if all_passed:
            self.passed += 1
            status = "PASS"
        else:
            self.failed += 1
            status = "FAIL"
        
        return {
            "sentence": sentence,
            "description": description,
            "expected": expected,
            "results": results,
            "status": status,
            "failures": failures
        }
    
    def run_all_tests(self) -> list:
        """Run all test cases."""
        tests = []
        
        # ====== Test 1: Negation Handling ======
        print("\n" + "="*60)
        print("TEST 1: Negation should reduce but not eliminate scores")
        print("="*60)
        
        t = self.test(
            "I am not caring about fairness",
            {"Care": (0.01, 0.2), "Equality": (0.01, 0.2)},
            "Negation should show reduced but visible bars"
        )
        tests.append(t)
        self._print_result(t)
        
        t = self.test(
            "We can never be good friends",
            {"Loyalty": (0.01, 0.2)},
            "Negation with 'never'"
        )
        tests.append(t)
        self._print_result(t)
        
        # ====== Test 2: Correlative "not only...but" ======
        print("\n" + "="*60)
        print("TEST 2: 'not only...but' is NOT negation")
        print("="*60)
        
        t = self.test(
            "You are not only my friend but my brother by heart",
            {"Loyalty": (0.1, 0.5), "Care": (0.1, 0.5)},
            "Correlative conjunction should give full scores"
        )
        tests.append(t)
        self._print_result(t)
        
        # ====== Test 3: Basic Positive Sentences ======
        print("\n" + "="*60)
        print("TEST 3: Positive sentences should show high scores")
        print("="*60)
        
        t = self.test(
            "I care about my family",
            {"Care": (0.2, 0.8), "Loyalty": (0.1, 0.8)},
            "Care + family"
        )
        tests.append(t)
        self._print_result(t)
        
        t = self.test(
            "We are good friends",
            {"Loyalty": (0.1, 0.5)},
            "Friends = Loyalty"
        )
        tests.append(t)
        self._print_result(t)
        
        t = self.test(
            "I love my brother and sister",
            {"Care": (0.2, 0.8), "Loyalty": (0.2, 0.8)},
            "Love + sibling"
        )
        tests.append(t)
        self._print_result(t)
        
        t = self.test(
            "fairness and justice are important",
            {"Equality": (0.2, 0.8)},
            "Fairness + justice"
        )
        tests.append(t)
        self._print_result(t)
        
        # ====== Test 4: Family Words ======
        print("\n" + "="*60)
        print("TEST 4: Family words should trigger Care + Loyalty")
        print("="*60)
        
        t = self.test(
            "my mother and father",
            {"Care": (0.1, 0.8), "Loyalty": (0.1, 0.8)},
            "Parents"
        )
        tests.append(t)
        self._print_result(t)
        
        t = self.test(
            "my son and daughter",
            {"Care": (0.1, 0.8), "Loyalty": (0.1, 0.8)},
            "Children"
        )
        tests.append(t)
        self._print_result(t)
        
        # ====== Test 5: Trust/Intimacy Words ======
        print("\n" + "="*60)
        print("TEST 5: Trust/intimacy words should trigger Care")
        print("="*60)
        
        t = self.test(
            "I trust you with my heart",
            {"Care": (0.1, 0.5)},
            "Trust + heart"
        )
        tests.append(t)
        self._print_result(t)
        
        t = self.test(
            "we are close friends",
            {"Care": (0.1, 0.5), "Loyalty": (0.1, 0.5)},
            "Close + friends"
        )
        tests.append(t)
        self._print_result(t)
        
        # ====== Test 6: Ally/Friend ======
        print("\n" + "="*60)
        print("TEST 6: Ally/Friend words")
        print("="*60)
        
        t = self.test(
            "you are my ally",
            {"Loyalty": (0.1, 0.8)},
            "Ally = Loyalty"
        )
        tests.append(t)
        self._print_result(t)
        
        t = self.test(
            "I got you as my companion",
            {"Loyalty": (0.1, 0.8)},
            "Companion = Loyalty"
        )
        tests.append(t)
        self._print_result(t)
        
        # ====== Summary ======
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        
        return tests
    
    def _print_result(self, result: dict):
        """Print individual test result."""
        status = result["status"]
        sentence = result["sentence"]
        failures = result.get("failures", [])
        
        if status == "PASS":
            print(f"[PASS] {sentence[:50]}...")
        else:
            print(f"[FAIL] {sentence[:50]}...")
            for f in failures:
                print(f"    - {f}")


def run_tests():
    """Run all tests."""
    print("="*60)
    print("MORAL SENTIMENT ANALYSIS - AUTOMATED TESTS")
    print("="*60)
    
    tester = MoralSentimentTester()
    results = tester.run_all_tests()
    
    return tester.passed, tester.failed


if __name__ == "__main__":
    run_tests()