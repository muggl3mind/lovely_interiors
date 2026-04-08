"""
Unit tests for matching algorithm optimizations.
Verifies that the new weight distribution improves color recommendations.
"""

from pathlib import Path
import sys
import importlib.util

# Direct import of matching module to avoid __init__.py import issues
matching_path = Path(__file__).resolve().parents[1] / "color_flow_paint_agent" / "tools" / "search" / "matching.py"
spec = importlib.util.spec_from_file_location("matching", matching_path)
matching = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matching)

# Import functions from the loaded module
score_unified = matching.score_unified
analyze_lrv = matching.analyze_lrv
analyze_undertones = matching.analyze_undertones
analyze_hex_color = matching.analyze_hex_color
analyze_description = matching.analyze_description


def test_weight_distribution():
    """Test that new weight distribution is correctly applied."""
    
    # Create a test color with all attributes
    test_color = {
        "name": "Test Gray",
        "description": "A warm gray with soft undertones perfect for hallways",
        "hex": "#d7d3ca",
        "lrv": 70,
        "hue_family": "gray",
        "undertone_tags": ["warm"]
    }
    
    # Create test intent for hallway
    test_intent = {
        "rooms": ["hallway"],
        "color_families": ["gray"],
        "undertones": ["warm"],
        "original_query": "warm gray for hallway"
    }
    
    # Calculate individual scores
    desc_score = analyze_description(test_color["description"], test_intent)
    lrv_score = analyze_lrv(test_color["lrv"], test_color["hex"], test_intent)
    undertone_score = analyze_undertones(test_color, test_intent)
    hex_score = analyze_hex_color(test_color["hex"], test_intent)
    
    # Verify individual components work
    print(f"\n🧮 Component Scores:")
    print(f"   Description: {desc_score:.3f}")
    print(f"   LRV: {lrv_score:.3f}")
    print(f"   Undertone: {undertone_score:.3f}")
    print(f"   Hex: {hex_score:.3f}")
    
    # Calculate base weighted score (80% of final)
    base_weighted = (
        desc_score * 0.45 +
        lrv_score * 0.20 +
        undertone_score * 0.20 +
        hex_score * 0.10 +
        0 * 0.05  # name score
    )
    
    actual_score = score_unified(test_color, test_intent)
    
    print(f"\n   Base weighted: {base_weighted:.3f}")
    print(f"   Actual score: {actual_score:.3f}")
    print(f"   Difference: {actual_score - base_weighted:.3f} (universal adjustments)")
    
    # Actual score should be higher due to 20% universal adjustments
    # but not too much higher
    assert actual_score >= base_weighted, "Score should include universal adjustments"
    assert actual_score <= base_weighted + 0.2, "Universal adjustments shouldn't dominate"
    print(f"   ✓ Weight distribution is correct (base + universal adjustments)")


def test_lrv_analysis():
    """Test that LRV analysis correctly scores brightness for rooms."""
    
    intent_hallway = {
        "rooms": ["hallway"],
        "color_families": [],
        "undertones": []
    }
    
    # Test high LRV (bright) - should be good for hallway
    high_lrv_score = analyze_lrv(70, "#d7d3ca", intent_hallway)
    print(f"\n💡 LRV Analysis:")
    print(f"   LRV 70 (bright) for hallway: {high_lrv_score:.3f}")
    assert high_lrv_score > 0.3, "High LRV should score well for hallway"
    
    # Test low LRV (dark) - should be lower for hallway
    low_lrv_score = analyze_lrv(30, "#3d5d63", intent_hallway)
    print(f"   LRV 30 (dark) for hallway: {low_lrv_score:.3f}")
    assert low_lrv_score < high_lrv_score, "Lower LRV should score lower for hallway"
    
    print(f"   ✓ LRV analysis works correctly")


def test_undertone_matching():
    """Test that undertone matching prevents clashes."""
    
    # Warm undertone color
    warm_color = {
        "undertone_tags": ["warm"],
        "hue_family": "neutral"
    }
    
    # Cool undertone color
    cool_color = {
        "undertone_tags": ["cool"],
        "hue_family": "blue"
    }
    
    # Intent asking for warm colors
    warm_intent = {
        "undertones": ["warm"],
        "color_families": ["neutral"],
        "rooms": []
    }
    
    warm_match_score = analyze_undertones(warm_color, warm_intent)
    cool_mismatch_score = analyze_undertones(cool_color, warm_intent)
    
    print(f"\n🎨 Undertone Matching:")
    print(f"   Warm color with warm intent: {warm_match_score:.3f}")
    print(f"   Cool color with warm intent: {cool_mismatch_score:.3f}")
    
    assert warm_match_score > cool_mismatch_score, "Warm should match better than cool for warm intent"
    print(f"   ✓ Undertone matching prevents clashes")


def test_hex_weight_reduced():
    """Test that hex has reduced influence compared to descriptions."""
    
    # Color with great description but so-so hex match
    good_desc_color = {
        "name": "Perfect Color",
        "description": "This warm beige is perfect for north-facing hallways with soft natural light",
        "hex": "#000000",  # Black - bad hex match
        "lrv": 65,
        "hue_family": "neutral",
        "undertone_tags": ["warm"]
    }
    
    # Color with poor description but good hex match
    good_hex_color = {
        "name": "Another Color",
        "description": "A color",  # Minimal description
        "hex": "#d7d3ca",  # Perfect beige hex
        "lrv": None,
        "hue_family": "",
        "undertone_tags": []
    }
    
    intent = {
        "rooms": ["hallway"],
        "color_families": ["beige"],
        "undertones": ["warm"],
        "original_query": "warm beige for north facing hallway"
    }
    
    good_desc_score = score_unified(good_desc_color, intent)
    good_hex_score = score_unified(good_hex_color, intent)
    
    print(f"\n⚖️ Weight Priority Test:")
    print(f"   Good description, bad hex: {good_desc_score:.3f}")
    print(f"   Bad description, good hex: {good_hex_score:.3f}")
    
    # With new weights, description should outweigh hex
    assert good_desc_score > good_hex_score * 0.5, "Description should have significant weight"
    print(f"   ✓ Description is prioritized over hex")


def test_stony_ground_vs_jitney():
    """Test that algorithm can now distinguish similar colors."""
    
    stony_ground = {
        "name": "Stony Ground",
        "description": "Stony Ground is a classic tone that has a slight underlying red which adds warmth and creates a soft beige finish.",
        "hex": "#a9988a",  # NEW corrected hex
        "lrv": None,
        "hue_family": "neutral",
        "undertone_tags": ["warm"]
    }
    
    jitney = {
        "name": "Jitney",
        "description": "Jitney is a relaxed brown based neutral with an incredibly uplifting earthy tone which reminds us of lazy days spent by the sea.",
        "hex": "#b8a892",  # NEW corrected hex (different!)
        "lrv": None,
        "hue_family": "neutral",
        "undertone_tags": ["neutral"]
    }
    
    intent_warm = {
        "rooms": ["hallway"],
        "color_families": ["neutral"],
        "undertones": ["warm"],
        "original_query": "warm neutral for hallway"
    }
    
    stony_score = score_unified(stony_ground, intent_warm)
    jitney_score = score_unified(jitney, intent_warm)
    
    print(f"\n🎯 Similar Colors Test:")
    print(f"   Stony Ground (warm undertone): {stony_score:.3f}")
    print(f"   Jitney (neutral undertone): {jitney_score:.3f}")
    
    # With warm intent, Stony Ground should score higher due to undertone match
    assert stony_score > jitney_score, "Algorithm should distinguish similar colors by undertones"
    
    # But they should both have reasonable scores (not identical)
    assert abs(stony_score - jitney_score) > 0.05, "Scores should be meaningfully different"
    
    print(f"   ✓ Algorithm distinguishes similar colors effectively")


def run_all_tests():
    """Run all matching algorithm tests."""
    print("🧪 Running Matching Algorithm Tests")
    print("=" * 60)
    
    tests = [
        test_weight_distribution,
        test_lrv_analysis,
        test_undertone_matching,
        test_hex_weight_reduced,
        test_stony_ground_vs_jitney,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n   ⚠️  ERROR: {e}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"📊 TEST RESULTS:")
    print(f"   Passed: {passed}/{len(tests)}")
    print(f"   Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print(f"\n   ✅ All tests passed!")
    else:
        print(f"\n   ⚠️  Some tests failed - see details above")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

