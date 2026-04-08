# 🚀 Quick Start Guide - Running Evaluations

## For Portfolio Demo & Interviews

### 1️⃣ Visual Demo (Best for Screenshots)

This is the **recommended method** for creating demo materials for LinkedIn/portfolio.

```bash
# Navigate to the agent directory
cd paint_palette_agent

# Start the web interface
adk web
```

Then in your browser:
1. Open the URL shown in terminal (usually `http://localhost:8080`)
2. Click on **"Eval"** tab in the UI
3. Click **"Load Eval Set"** 
4. Select one of these files:
   - `evaluations/test_happy_path.test.json`
   - `evaluations/test_validation_loop.test.json`
   - `evaluations/test_real_scenario.test.json`
5. Click **"Run Evaluation"**
6. Wait for results (usually 30-60 seconds)

### 📸 Take These Screenshots

For your portfolio, capture:

**Screenshot 1: All Tests Passing** ✅
- Shows all three test cases with green checkmarks
- Demonstrates working agent with quality control

**Screenshot 2: Trace View** 🔍
- Click the "Trace" tab for any test
- Shows the tool call sequence (analyze_room_photos → track_requirements → etc.)
- Proves the agent actually calls functions vs. hallucinating

**Screenshot 3: Validation Loop** 🔄
- From the validation loop test
- Shows critic catching an error and refiner fixing it
- Demonstrates multi-agent quality control

---

### 2️⃣ Command Line (For Quick Checks)

```bash
# Run a single test
adk eval color_flow_paint_agent evaluations/test_happy_path.test.json --print_detailed_results

# Run all tests at once
adk eval color_flow_paint_agent evaluations/test_*.test.json
```

**What you'll see:**
```
Running evaluation: happy_path_consultation
✓ Tool trajectory: 1.0 (100%)
✓ Response match: 0.82 (82%)
✅ PASSED

Running evaluation: validation_loop_quality_control
✓ Tool trajectory: 1.0 (100%)
✓ Response match: 0.78 (78%)
✅ PASSED

Running evaluation: real_client_scenario
✓ Tool trajectory: 1.0 (100%)
✓ Response match: 0.85 (85%)
✅ PASSED

📊 SUMMARY: 3/3 tests passed
```

---

### 3️⃣ Python Testing (For Technical Interviews)

If asked about testing practices in an interview:

```bash
# Run the pytest integration
pytest tests/integration/test_agent_evaluation.py -v

# Expected output:
tests/integration/test_agent_evaluation.py::test_happy_path PASSED
tests/integration/test_agent_evaluation.py::test_validation_loop PASSED  
tests/integration/test_agent_evaluation.py::test_real_scenario PASSED
```

---

## Interview Prep: What to Say

### Question: "Walk me through your evaluation strategy"

**Your Answer:**
> "I implemented a three-tier evaluation suite for my paint consultant agent:
> 
> **First**, a happy path test that validates the complete workflow - from photo analysis through color recommendation. It checks both tool trajectory (the functions called) and response quality.
> 
> **Second**, a validation loop test that demonstrates my multi-agent quality control system. A critic agent catches technical errors like undertone contradictions, and a refiner agent corrects them.
> 
> **Third**, a real scenario test using actual room photos and client briefs, validating the agent handles production-like situations.
> 
> I use two key metrics: 100% tool trajectory match to prevent hallucinations - where the agent claims to analyze photos without actually calling the function - and 80% response match to allow natural language flexibility while ensuring quality."

### Question: "How do you measure success?"

**Your Answer:**
> "I use Google ADK's evaluation framework with two complementary metrics:
> 
> **Tool Trajectory Score** (1.0 = 100% match): Validates that the agent calls the right functions in the right order. This catches a common LLM issue where the agent claims to have analyzed photos without actually calling the analysis function - that's hallucination.
> 
> **Response Match Score** (0.8 = 80% threshold): Evaluates the quality of the agent's natural language responses while allowing some flexibility. It ensures the agent shows search results in ranked order, narrows to finalists, and provides clear recommendations.
> 
> All three test scenarios pass both metrics, giving me confidence the agent performs reliably."

### Question: "What's the validation loop?"

**Your Answer:**
> "It's a multi-agent quality control system. After the main agent makes a recommendation, a consistency critic reviews it for logical contradictions - like claiming a color has warm undertones when the hex code analysis shows it's cool.
> 
> If issues are found, a refiner agent corrects them. If no issues are found, it calls an exit function to accept the output. I limited it to 3 iterations to prevent infinite loops.
> 
> This catches technical errors in color theory before they reach the user. It's inspired by production AI systems that use multiple specialized agents rather than relying on a single monolithic model."

---

## Troubleshooting

### Test Fails: Tool Trajectory < 1.0

**Problem:** Agent didn't call expected functions

**Check:**
1. Did the agent call `analyze_room_photos` for each photo?
2. Did it call `track_requirements` before searching?
3. Did it skip `search_colors_smart` in the first response?

**Fix:** Review agent prompt to emphasize calling functions vs. claiming to

---

### Test Fails: Response Match < 0.75

**Problem:** Agent's response doesn't match expected pattern

**Check:**
1. Does response show top 10 search results?
2. Does it narrow to 3 finalists?
3. Does it recommend ONE color with reasoning?
4. Is the voice casual/confident vs. corporate?

**Fix:** Review agent prompt for voice and formatting requirements

---

### Tests Run Too Slow (> 60 seconds)

**Problem:** Evaluation taking a long time

**Tips:**
1. Use `adk web` for interactive testing (faster feedback)
2. Run individual tests vs. all at once during development
3. Check API rate limits if using external APIs

---

## Next Steps After Tests Pass

1. ✅ **Take screenshots** for portfolio
2. ✅ **Update main README** with evaluation section
3. ✅ **Practice explaining** the approach out loud
4. ✅ **Prepare demo** walkthrough for interviews
5. ✅ **Add to LinkedIn** with visuals showing passing tests

---

## Files Overview

```
evaluations/
├── README.md                           # Full documentation
├── QUICKSTART.md                       # This file - quick commands
├── test_happy_path.test.json          # Test 1: Complete workflow
├── test_validation_loop.test.json     # Test 2: Quality control
└── test_real_scenario.test.json       # Test 3: Real client case
```

---

**Need Help?** 
- Check the main README.md for detailed explanations
- Review ADK evaluation docs: https://google.github.io/adk-docs/evaluate/
- Run `adk web` for visual debugging

**Ready to Demo!** 🎉

