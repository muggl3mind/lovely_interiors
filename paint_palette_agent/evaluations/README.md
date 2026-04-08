# 🧪 Agent Evaluation Suite

## Overview

This evaluation suite validates the **Color Flow Paint Agent** using Google ADK's evaluation framework. It tests both the **tool usage trajectory** (what functions the agent calls) and **response quality** (what it says to users).

## Why Evaluate?

LLM agents can exhibit inconsistent behavior due to their probabilistic nature. Unlike traditional software where unit tests provide binary pass/fail signals, AI agents require:

1. **Trajectory Evaluation**: Verify the agent calls the right tools in the right order
2. **Response Quality Evaluation**: Assess the quality and accuracy of recommendations

This evaluation framework catches common issues like:
- ❌ Claiming to analyze photos without calling the function (hallucination)
- ❌ Making recommendations before gathering requirements
- ❌ Technical errors in color theory (undertone contradictions)
- ❌ Skipping critical workflow steps

## Test Cases

### 1️⃣ Happy Path Test (`test_happy_path.test.json`)

**What it validates:** Complete consultation workflow executing correctly

**Scenario:**
- User provides room photo and asks for paint recommendation
- Agent analyzes photo → Tracks requirements → Asks clarifying question
- User answers question
- Agent searches colors → Recommends palette

**Why it matters:** Validates the core agent workflow works end-to-end

**Expected trajectory:**
```
Turn 1: analyze_room_photos → track_requirements → [Question to user]
Turn 2: track_requirements → search_colors_smart → [Recommendation]
```

---

### 2️⃣ Validation Loop Test (`test_validation_loop.test.json`)

**What it validates:** Multi-agent validation system catches and fixes errors

**Scenario:**
- Agent makes a color recommendation
- Consistency critic detects an undertone error
- Refiner agent corrects the mistake

**Why it matters:** Demonstrates sophisticated quality control and self-correction

**Expected behavior:**
```
Recommendation Agent → Makes recommendation (with error)
Consistency Critic → Identifies: "Claimed warm but hex shows cool"
Refiner Agent → Corrects the undertone claim
```

---

### 3️⃣ Real Scenario Test (`test_real_scenario.test.json`)

**What it validates:** Agent handles actual use case with real room photos

**Scenario:**
- User provides photo of actual hallway from project
- User describes specific style preferences (French cottage, warm neutrals)
- Agent provides comprehensive recommendations from Farrow & Ball catalog

**Why it matters:** Shows real-world application with concrete results

**Expected outcome:**
- Analyzes actual room conditions
- Recommends appropriate Farrow & Ball colors
- Explains flow and undertone consistency

---

## Evaluation Criteria

### Tool Trajectory Score (1.0 = 100% match required)
Validates that the agent:
- ✅ Calls `analyze_room_photos()` for each photo
- ✅ Calls `track_requirements()` before making recommendations
- ✅ Does NOT call `search_colors_smart()` until requirements are gathered
- ✅ Actually calls functions instead of claiming to

### Response Match Score (0.8 = 80% similarity allowed)
Validates that the agent:
- ✅ Uses casual, confident voice (not corporate)
- ✅ Shows search results in ranked order
- ✅ Narrows to finalists with tradeoffs
- ✅ Recommends one color with clear reasoning

---

## How to Run Evaluations

### Option 1: Visual Interface (Recommended for Demo)

1. **Start the ADK web interface:**
   ```bash
   cd paint_palette_agent
   adk web
   ```

2. **Navigate to the Eval tab in the UI**

3. **Load an evaluation set:**
   - Click "Load Eval Set"
   - Select one of the `.test.json` files
   - Click "Run Evaluation"

4. **View results:**
   - ✅ Green = Passed
   - ❌ Red = Failed (click to see details)
   - 📊 View trace for detailed tool call history

5. **Take screenshots** for portfolio:
   - All tests passing ✅
   - Trace view showing correct tool sequence
   - Validation loop catching an error

### Option 2: Command Line (For Automation)

```bash
# Run a single test
adk eval color_flow_paint_agent evaluations/test_happy_path.test.json --print_detailed_results

# Run all tests
adk eval color_flow_paint_agent evaluations/*.test.json
```

### Option 3: Python Testing (For CI/CD)

```bash
pytest tests/integration/test_agent_evaluation.py -v
```

---

## Test Results

### Expected Outcomes

All three tests should **PASS** with these scores:

| Test | Tool Trajectory | Response Match | Status |
|------|----------------|----------------|--------|
| Happy Path | 1.0 (100%) | ≥ 0.8 (80%) | ✅ PASS |
| Validation Loop | 1.0 (100%) | ≥ 0.8 (80%) | ✅ PASS |
| Real Scenario | 1.0 (100%) | ≥ 0.8 (80%) | ✅ PASS |

### Common Failures & Fixes

**❌ Tool Trajectory Failed (Score < 1.0)**
- **Issue**: Agent claimed to analyze photos but didn't call the function
- **Fix**: Update prompt to emphasize "ACTUALLY CALL THE FUNCTION"

**❌ Response Match Failed (Score < 0.8)**
- **Issue**: Agent's response doesn't match expected pattern
- **Fix**: Check if response includes required elements (search results, finalists, recommendation)

**❌ Validation Loop Didn't Catch Error**
- **Issue**: Critic failed to identify undertone contradiction
- **Fix**: Improve critic instruction with more specific validation rules

---

## Portfolio Value

This evaluation suite demonstrates:

✅ **Modern AI Engineering**: Using industry-standard evaluation frameworks  
✅ **Quality Assurance**: Systematic testing of agent behavior  
✅ **Multi-Agent Architecture**: Sophisticated validation loops  
✅ **Production Thinking**: Preventing hallucinations and ensuring consistency  
✅ **Technical Depth**: Understanding trajectory vs. response evaluation  

---

## Interview Talking Points

**"Why did you add evaluation?"**
> "LLM agents are probabilistic and can hallucinate - claiming to call functions without actually calling them. I implemented trajectory evaluation to verify the agent's tool usage and response quality evaluation to ensure accurate recommendations. This catches issues before they reach users."

**"What's the validation loop?"**
> "It's a multi-agent system where a critic agent reviews recommendations for logical contradictions - like claiming a color has a warm undertone when the hex code shows it's cool. A refiner agent then corrects any errors. It's self-checking quality control."

**"How do you measure success?"**
> "I use two metrics: 100% tool trajectory match to ensure correct function calls, and 80% response match to allow natural language flexibility while maintaining quality. All three test scenarios validate different aspects of the consultation workflow."

---

## Next Steps

To extend this evaluation suite:

1. **Add edge case tests**: User changes mind, conflicting preferences
2. **Add performance benchmarks**: Response time, token usage
3. **Add safety tests**: Inappropriate requests, out-of-scope queries
4. **Integrate with CI/CD**: Run tests on every commit

---

**Built with Google ADK Evaluation Framework**  
*Demonstrates modern AI agent quality assurance practices*

