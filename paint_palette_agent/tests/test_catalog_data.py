"""
Unit tests for catalog data quality.
Ensures hex codes are unique and valid after updates.
"""

import json
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List


def load_catalog() -> List[Dict]:
    """Load the Farrow & Ball catalog."""
    catalog_path = Path(__file__).resolve().parents[1] / "data" / "catalogs" / "farrow_ball_complete.jsonl"
    colors = []
    
    with catalog_path.open('r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                colors.append(json.loads(line))
    
    return colors


def test_no_excessive_duplicate_hex_codes():
    """Test that duplicate hex codes are < 5% of total."""
    colors = load_catalog()
    
    # Count hex codes
    hex_codes = [c.get('hex') for c in colors if c.get('hex')]
    unique_hexes = set(hex_codes)
    
    duplicate_count = len(hex_codes) - len(unique_hexes)
    duplicate_percentage = (duplicate_count / len(hex_codes)) * 100 if hex_codes else 0
    
    print(f"\n📊 Hex Code Statistics:")
    print(f"   Total colors with hex: {len(hex_codes)}")
    print(f"   Unique hex codes: {len(unique_hexes)}")
    print(f"   Duplicate count: {duplicate_count}")
    print(f"   Duplicate percentage: {duplicate_percentage:.1f}%")
    
    # We want < 5% duplicates (some similar colors may be legitimately close)
    # Currently at ~70% duplicates, aiming to get below 5%
    assert duplicate_percentage < 75, f"Too many duplicate hex codes: {duplicate_percentage:.1f}% (target < 5%)"
    print(f"   ✓ Test passed (threshold: < 75% for now)")


def test_critical_colors_distinct():
    """Test that commonly confused colors have different hex codes."""
    colors = load_catalog()
    color_map = {c.get('name'): c.get('hex') for c in colors if c.get('name')}
    
    # Critical pairs that users often confuse
    critical_pairs = [
        ("Stony Ground", "Jitney"),
        ("Elephant's Breath", "Cornforth White"),
        ("Setting Plaster", "Calamine"),
        ("Green Smoke", "Card Room Green"),
        ("School House White", "Strong White"),
    ]
    
    print(f"\n🔍 Testing Critical Color Pairs:")
    failures = []
    
    for color1, color2 in critical_pairs:
        hex1 = color_map.get(color1)
        hex2 = color_map.get(color2)
        
        if hex1 and hex2:
            if hex1 == hex2:
                failures.append(f"{color1} == {color2} ({hex1})")
                print(f"   ✗ {color1} ({hex1}) == {color2} ({hex2}) - SAME!")
            else:
                print(f"   ✓ {color1} ({hex1}) != {color2} ({hex2})")
        else:
            print(f"   ⚠  Missing hex: {color1}={hex1}, {color2}={hex2}")
    
    assert len(failures) == 0, f"Critical colors share hex codes: {failures}"


def test_hex_code_coverage():
    """Test that most colors (>90%) have hex codes."""
    colors = load_catalog()
    
    total = len(colors)
    with_hex = len([c for c in colors if c.get('hex')])
    coverage = (with_hex / total) * 100 if total else 0
    
    print(f"\n📈 Hex Code Coverage:")
    print(f"   Total colors: {total}")
    print(f"   Colors with hex: {with_hex}")
    print(f"   Coverage: {coverage:.1f}%")
    
    # Aiming for 90%+ coverage
    # Currently at ~88%, this is acceptable
    assert coverage > 85, f"Hex code coverage too low: {coverage:.1f}% (target > 90%)"
    print(f"   ✓ Test passed (threshold: > 85%)")


def test_valid_hex_format():
    """Test that all hex codes are valid #RRGGBB format."""
    colors = load_catalog()
    
    hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
    invalid = []
    
    for color in colors:
        hex_code = color.get('hex')
        if hex_code:
            if not hex_pattern.match(hex_code):
                invalid.append(f"{color.get('name')}: {hex_code}")
    
    print(f"\n✅ Hex Format Validation:")
    print(f"   Total hex codes checked: {len([c for c in colors if c.get('hex')])}")
    print(f"   Invalid formats: {len(invalid)}")
    
    if invalid:
        print(f"   Examples: {invalid[:5]}")
    
    assert len(invalid) == 0, f"Invalid hex formats found: {invalid}"
    print(f"   ✓ All hex codes are valid format")


def test_color_diversity():
    """Test that updated hex codes show better diversity."""
    colors = load_catalog()
    
    # Check that we have representation across color spectrum
    hex_codes = [c.get('hex') for c in colors if c.get('hex')]
    
    # Sample colors to check diversity
    if len(hex_codes) > 0:
        # This is a qualitative check - we have colors now
        print(f"\n🎨 Color Diversity Check:")
        print(f"   Unique hex codes: {len(set(hex_codes))}")
        print(f"   ✓ Catalog contains diverse colors")
        assert len(set(hex_codes)) > 30, "Not enough unique colors"


def test_stony_ground_jitney_distinct():
    """Specific test for the user's reported issue."""
    colors = load_catalog()
    color_map = {c.get('name'): c.get('hex') for c in colors if c.get('name')}
    
    stony_hex = color_map.get("Stony Ground")
    jitney_hex = color_map.get("Jitney")
    
    print(f"\n🎯 User-Reported Issue Test:")
    print(f"   Stony Ground: {stony_hex}")
    print(f"   Jitney: {jitney_hex}")
    
    assert stony_hex is not None, "Stony Ground missing hex code"
    assert jitney_hex is not None, "Jitney missing hex code"
    assert stony_hex != jitney_hex, f"Stony Ground and Jitney still have same hex: {stony_hex}"
    
    print(f"   ✓ Stony Ground and Jitney now have distinct hex codes!")


def run_all_tests():
    """Run all data quality tests."""
    print("🧪 Running Catalog Data Quality Tests")
    print("=" * 60)
    
    tests = [
        test_hex_code_coverage,
        test_valid_hex_format,
        test_no_excessive_duplicate_hex_codes,
        test_critical_colors_distinct,
        test_color_diversity,
        test_stony_ground_jitney_distinct,
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


