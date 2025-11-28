"""
LLM Training Validation Script for ARIA
Tests command classification accuracy using the training dataset
"""

import json
from typing import Dict, List, Tuple
from brain import AriaBrain
from command_intent_classifier import CommandIntentClassifier


def load_training_dataset(filepath: str = "llm_training_dataset.json") -> Dict:
    """Load the training dataset"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return {}


def test_intent_classification(classifier: CommandIntentClassifier, dataset: Dict) -> Tuple[int, int, List[Dict]]:
    """
    Test classification accuracy on the training dataset
    Returns: (correct_count, total_count, failed_examples)
    """
    correct = 0
    total = 0
    failed = []
    
    for category_data in dataset.get("training_examples", []):
        category = category_data.get("category", "unknown")
        expected_intent = category_data.get("intent", "")
        
        for example in category_data.get("examples", []):
            # Test main input
            test_input = example.get("input", "")
            if test_input:
                total += 1
                result = classifier.classify_intent(test_input)
                
                if result["intent"] == expected_intent:
                    correct += 1
                else:
                    failed.append({
                        "input": test_input,
                        "expected": expected_intent,
                        "got": result["intent"],
                        "confidence": result.get("confidence", 0),
                        "category": category
                    })
            
            # Test variations
            for variation in example.get("variations", []):
                total += 1
                result = classifier.classify_intent(variation)
                
                if result["intent"] == expected_intent:
                    correct += 1
                else:
                    failed.append({
                        "input": variation,
                        "expected": expected_intent,
                        "got": result["intent"],
                        "confidence": result.get("confidence", 0),
                        "category": category
                    })
    
    return correct, total, failed


def test_parameter_extraction(classifier: CommandIntentClassifier) -> None:
    """Test parameter extraction accuracy"""
    test_cases = [
        {
            "input": "set volume to 75",
            "expected_params": {"level": 75}
        },
        {
            "input": "create file notes.txt on desktop",
            "expected_params": {"filename": "notes.txt", "location": "desktop"}
        },
        {
            "input": "what's the weather in London",
            "expected_params": {"city": "London"}
        },
        {
            "input": "copy hello world to clipboard",
            "expected_params": {"text": "hello world"}
        },
        {
            "input": "search for *.pdf in downloads",
            "expected_params": {"pattern": "*.pdf", "location": "downloads"}
        }
    ]
    
    print("\n" + "="*70)
    print("PARAMETER EXTRACTION TESTS")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        result = classifier.classify_intent(test["input"])
        params = result.get("parameters", {})
        expected = test["expected_params"]
        
        match = all(params.get(k) == v for k, v in expected.items())
        status = "✓ PASS" if match else "✗ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"  Input: {test['input']}")
        print(f"  Expected: {expected}")
        print(f"  Got: {params}")


def test_edge_cases(classifier: CommandIntentClassifier) -> None:
    """Test edge cases and potential confusion points"""
    test_cases = [
        {
            "input": "find resume on desktop",
            "expected": "file_search",
            "description": "File search vs web search"
        },
        {
            "input": "search for python tutorials",
            "expected": "web_search",
            "description": "Web search vs file search"
        },
        {
            "input": "open Chrome",
            "expected": "app_open",
            "description": "App vs website"
        },
        {
            "input": "open YouTube",
            "expected": "web_open",
            "description": "Website vs app"
        },
        {
            "input": "create hi.txt in download section",
            "expected": "file_create",
            "description": "Location mapping (download section -> downloads)"
        }
    ]
    
    print("\n" + "="*70)
    print("EDGE CASE TESTS")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        result = classifier.classify_intent(test["input"])
        intent = result.get("intent", "")
        
        match = intent == test["expected"]
        status = "✓ PASS" if match else "✗ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"  Description: {test['description']}")
        print(f"  Input: {test['input']}")
        print(f"  Expected: {test['expected']}")
        print(f"  Got: {intent}")
        if not match:
            print(f"  Confidence: {result.get('confidence', 0)}")


def main():
    """Run all validation tests"""
    print("="*70)
    print("ARIA LLM TRAINING VALIDATION")
    print("="*70)
    
    # Initialize brain and classifier
    print("\nInitializing ARIA Brain and Classifier...")
    brain = AriaBrain()
    classifier = CommandIntentClassifier(brain)
    
    if not brain.is_available():
        print("ERROR: No LLM available. Please check your API keys.")
        return
    
    # Load training dataset
    print("Loading training dataset...")
    dataset = load_training_dataset()
    
    if not dataset:
        print("ERROR: Could not load training dataset.")
        return
    
    print(f"Dataset loaded: {dataset['metadata']['total_examples']} examples")
    print(f"Categories: {len(dataset['metadata']['categories'])}")
    print(f"Intents: {dataset['metadata']['total_intents']}")
    
    # Run intent classification tests
    print("\n" + "="*70)
    print("INTENT CLASSIFICATION TESTS")
    print("="*70)
    print("\nTesting intent classification accuracy...")
    
    correct, total, failed = test_intent_classification(classifier, dataset)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\nResults:")
    print(f"  Total Tests: {total}")
    print(f"  Correct: {correct}")
    print(f"  Failed: {len(failed)}")
    print(f"  Accuracy: {accuracy:.2f}%")
    
    # Show failed examples
    if failed:
        print(f"\n{'='*70}")
        print(f"FAILED CLASSIFICATIONS ({len(failed)} total)")
        print("="*70)
        
        # Group by category
        failed_by_category = {}
        for fail in failed[:10]:  # Show first 10
            cat = fail["category"]
            if cat not in failed_by_category:
                failed_by_category[cat] = []
            failed_by_category[cat].append(fail)
        
        for cat, failures in failed_by_category.items():
            print(f"\nCategory: {cat}")
            for fail in failures:
                print(f"  Input: {fail['input']}")
                print(f"  Expected: {fail['expected']} | Got: {fail['got']}")
                print(f"  Confidence: {fail['confidence']:.2f}")
    
    # Run parameter extraction tests
    test_parameter_extraction(classifier)
    
    # Run edge case tests
    test_edge_cases(classifier)
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Intent Classification Accuracy: {accuracy:.2f}%")
    
    if accuracy >= 95:
        print("✓ EXCELLENT: Training is highly effective!")
    elif accuracy >= 85:
        print("✓ GOOD: Training is effective, minor improvements possible")
    elif accuracy >= 75:
        print("⚠ FAIR: Consider reviewing failed cases and adding more training data")
    else:
        print("✗ NEEDS IMPROVEMENT: Significant training issues detected")
    
    print("\nTest complete!")


if __name__ == "__main__":
    main()
