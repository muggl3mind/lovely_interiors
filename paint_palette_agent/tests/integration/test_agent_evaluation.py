"""
Integration tests for Color Flow Paint Agent evaluation.
Runs the three core evaluation test cases programmatically using pytest.
"""

import pytest
from pathlib import Path
from google.adk.evaluation.agent_evaluator import AgentEvaluator


# Test data directory
EVALUATIONS_DIR = Path(__file__).resolve().parents[2] / "evaluations"


@pytest.mark.asyncio
async def test_happy_path():
    """
    Test 1: Happy Path Consultation
    
    Validates the complete paint consultation workflow executes correctly:
    - Turn 1: User provides photo + brief → Agent analyzes + tracks + asks question
    - Turn 2: User answers → Agent searches + recommends
    
    Success Criteria:
    - Tool trajectory: 1.0 (100% match)
    - Response match: ≥ 0.75 (75% similarity)
    """
    test_file = EVALUATIONS_DIR / "test_happy_path.test.json"
    
    assert test_file.exists(), f"Test file not found: {test_file}"
    
    await AgentEvaluator.evaluate(
        agent_module="color_flow_paint_agent",
        eval_dataset_file_path_or_dir=str(test_file),
    )
    
    # If evaluate() doesn't raise an exception, the test passed
    print("✅ Happy path test PASSED")


@pytest.mark.asyncio
async def test_validation_loop():
    """
    Test 2: Validation Loop Quality Control
    
    Validates the multi-agent validation system catches and corrects errors:
    - Consistency critic detects undertone contradictions
    - Refiner agent corrects technical errors
    - Quality control prevents incorrect recommendations
    
    Success Criteria:
    - Tool trajectory: 1.0 (100% match)
    - Response match: ≥ 0.75 (75% similarity)
    - Rubric: Undertone claims match hex code analysis
    """
    test_file = EVALUATIONS_DIR / "test_validation_loop.test.json"
    
    assert test_file.exists(), f"Test file not found: {test_file}"
    
    await AgentEvaluator.evaluate(
        agent_module="color_flow_paint_agent",
        eval_dataset_file_path_or_dir=str(test_file),
    )
    
    print("✅ Validation loop test PASSED")


@pytest.mark.asyncio
async def test_real_scenario():
    """
    Test 3: Real Client Scenario
    
    Validates agent handling of actual client brief with multiple rooms:
    - Analyzes 4 room photos
    - Tracks comprehensive requirements
    - Provides complete palette with flow explanation
    - Addresses all rooms with appropriate Farrow & Ball colors
    
    Success Criteria:
    - Tool trajectory: 1.0 (100% match)
    - Response match: ≥ 0.70 (70% similarity)
    - Rubric: All rooms addressed, colors explained, proper tool usage
    """
    test_file = EVALUATIONS_DIR / "test_real_scenario.test.json"
    
    assert test_file.exists(), f"Test file not found: {test_file}"
    
    await AgentEvaluator.evaluate(
        agent_module="color_flow_paint_agent",
        eval_dataset_file_path_or_dir=str(test_file),
    )
    
    print("✅ Real scenario test PASSED")


@pytest.mark.asyncio
async def test_all_evaluations():
    """
    Run all three evaluation tests in sequence.
    
    This is a convenience test that runs all evaluations together
    and provides a summary at the end.
    """
    tests = [
        ("Happy Path", test_happy_path),
        ("Validation Loop", test_validation_loop),
        ("Real Scenario", test_real_scenario),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            await test_func()
            results.append((test_name, "PASSED"))
        except Exception as e:
            results.append((test_name, f"FAILED: {e}"))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("=" * 60)
    
    for test_name, status in results:
        emoji = "✅" if "PASSED" in status else "❌"
        print(f"{emoji} {test_name}: {status}")
    
    passed = sum(1 for _, status in results if "PASSED" in status)
    total = len(results)
    
    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 60)
    
    # Fail the test if any sub-test failed
    assert passed == total, f"Only {passed}/{total} tests passed"


def test_evaluation_files_exist():
    """
    Sanity check: Verify all evaluation test files exist.
    """
    required_files = [
        "test_happy_path.test.json",
        "test_validation_loop.test.json",
        "test_real_scenario.test.json",
        "README.md",
        "QUICKSTART.md",
    ]
    
    missing_files = []
    
    for filename in required_files:
        filepath = EVALUATIONS_DIR / filename
        if not filepath.exists():
            missing_files.append(filename)
    
    assert not missing_files, f"Missing evaluation files: {', '.join(missing_files)}"
    print(f"✅ All {len(required_files)} evaluation files found")


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    import asyncio
    
    print("🧪 Running Color Flow Paint Agent Evaluation Tests\n")
    
    # Run the all-in-one test
    asyncio.run(test_all_evaluations())

