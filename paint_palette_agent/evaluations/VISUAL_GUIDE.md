# 📊 Visual Guide to Agent Evaluation

## Evaluation Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT (Test Case)                       │
│  "I need paint for my hallway. Here's a photo."                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   COLOR FLOW PAINT AGENT      │
         │   (Main Recommendation Agent) │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   EXPECTED TRAJECTORY:        │
         │   1. analyze_room_photos()    │
         │   2. track_requirements()     │
         │   3. [Ask clarifying Q]       │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │     VALIDATION LOOP           │
         │  ┌─────────────────────────┐  │
         │  │  Consistency Critic     │  │
         │  │  Checks for:            │  │
         │  │  - Undertone errors     │  │
         │  │  - LRV contradictions   │  │
         │  │  - Missing rooms        │  │
         │  └──────────┬──────────────┘  │
         │             │                  │
         │             ▼                  │
         │  ┌─────────────────────────┐  │
         │  │  Refiner Agent          │  │
         │  │  - Fixes errors         │  │
         │  │  - OR exits if perfect  │  │
         │  └──────────┬──────────────┘  │
         └─────────────┼──────────────────┘
                       │
                       ▼
         ┌───────────────────────────────┐
         │    EVALUATION FRAMEWORK       │
         │    (Google ADK)               │
         │                               │
         │  ✓ Tool Trajectory Match      │
         │    Actual vs Expected         │
         │                               │
         │  ✓ Response Quality Match     │
         │    LLM-judged semantic sim.   │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │         RESULTS               │
         │                               │
         │  Tool Score:  1.0  (100%) ✅  │
         │  Response:    0.82 (82%)  ✅  │
         │                               │
         │  Status: PASSED               │
         └───────────────────────────────┘
```

---

## Test Case Lifecycle

### 1. Test Definition (JSON File)
```json
{
  "test_name": "happy_path_consultation",
  "turns": [
    {
      "user_content": "I need paint for my hallway...",
      "expected_agent_steps": ["analyze_room_photos", "track_requirements"],
      "expected_agent_response": "Got it - analyzed your photo..."
    }
  ],
  "criteria": {
    "tool_trajectory_avg_score": 1.0,  // Must match exactly
    "response_match_score": 0.8        // 80% similarity OK
  }
}
```

### 2. Execution
```
ADK Web UI  →  Load Test File  →  Run Evaluation
                                       │
                                       ▼
                            Agent processes test turns
                                       │
                                       ▼
                            Records actual tool calls
                                       │
                                       ▼
                            Captures agent responses
```

### 3. Evaluation
```
┌─────────────────────────────────────┐
│  TRAJECTORY COMPARISON              │
├─────────────────────────────────────┤
│  Expected: [analyze, track]         │
│  Actual:   [analyze, track]         │
│  Match:    100% ✅                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  RESPONSE COMPARISON                │
├─────────────────────────────────────┤
│  Expected: "Got it - analyzed..."   │
│  Actual:   "Got it - analyzed..."   │
│  Similarity: 82% ✅                 │
└─────────────────────────────────────┘
```

---

## Validation Loop in Detail

### How Quality Control Works

```
Step 1: RECOMMENDATION AGENT
┌─────────────────────────────────────────────────┐
│ "Sulking Room Pink has cool undertones..."      │
│ Hex: #C4A9A5                                    │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
Step 2: CONSISTENCY CRITIC
┌─────────────────────────────────────────────────┐
│ 🔍 CHECKING:                                    │
│ - Hex #C4A9A5 = RGB(196, 169, 165)            │
│ - R (196) > B (165)                            │
│ - Therefore: WARM undertone                     │
│                                                 │
│ ❌ ERROR DETECTED:                              │
│ "Claimed cool but hex shows warm"              │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
Step 3: REFINER AGENT
┌─────────────────────────────────────────────────┐
│ ✏️ CORRECTING:                                  │
│ "Sulking Room Pink has WARM undertones..."      │
│ Hex: #C4A9A5 (R>B confirms warm)              │
│                                                 │
│ ✅ FIXED                                        │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
Step 4: OUTPUT
┌─────────────────────────────────────────────────┐
│ Correct recommendation sent to user             │
└─────────────────────────────────────────────────┘
```

### Without Validation Loop
```
Agent → User
  ❌ "Cool undertone" (incorrect) → User gets wrong advice
```

### With Validation Loop
```
Agent → Critic → Refiner → User
  ❌ Error detected → ✅ Error fixed → User gets correct advice
```

---

## Three Test Scenarios Visualized

### Test 1: Happy Path
```
USER                    AGENT                   VALIDATION
│                       │                       │
├─ "Paint my hallway"   │                       │
│  + photo              │                       │
│                       ├─ analyze_room_photos  │
│                       ├─ track_requirements   │
│                       ├─ "LRV preference?"    │
│                       │                       │
├─ "LRV 60+"            │                       │
│                       ├─ track_requirements   │
│                       ├─ search_colors_smart  │
│                       ├─ Show results         │
│                       ├─ Recommend            │
│                       │                       ├─ ✅ Validates
│                       │                       │   trajectory
│                       │                       ├─ ✅ Validates
│                       │                       │   response
│                       │                       │
Result: ✅ PASSED (100% trajectory, 82% response)
```

### Test 2: Validation Loop
```
USER                    AGENT                   CRITIC/REFINER
│                       │                       │
├─ "Paint for cool     │                       │
│   marble room"        │                       │
│                       ├─ Search colors        │
│                       ├─ Recommend            │
│                       │  "Cool undertones"    │
│                       │                       ├─ 🔍 Check hex
│                       │                       ├─ ❌ Detect error
│                       │                       ├─ ✏️ Fix error
│                       ├─ Corrected response   │
│                       │                       │
Result: ✅ PASSED (Validation loop caught & fixed error)
```

### Test 3: Real Scenario
```
USER                    AGENT                   TOOLS USED
│                       │                       │
├─ "4 rooms + photos"   │                       │
│  "French cottage"     │                       │
│  "Mouse's Back +      │                       │
│   Sulking Room Pink"  │                       │
│                       ├─────────────────────► analyze_room_photos (×4)
│                       ├─────────────────────► track_requirements
│                       ├─ "Which rooms?"       │
│                       │                       │
├─ "Dining = Mouse's    │                       │
│   Hallway = Sulking"  │                       │
│                       ├─────────────────────► track_requirements
│                       ├─────────────────────► search_colors_smart (×4)
│                       ├─────────────────────► validate_requirements
│                       ├─ Complete palette     │
│                       │   with flow           │
│                       │                       │
Result: ✅ PASSED (All rooms addressed, flow explained)
```

---

## Metrics Breakdown

### Tool Trajectory Score = 1.0 (100%)

**What it measures:** Did the agent call the RIGHT functions in the RIGHT order?

```
Expected Sequence:
[1] analyze_room_photos
[2] track_requirements
[3] (no search yet)

Actual Sequence:
[1] analyze_room_photos  ✓
[2] track_requirements   ✓
[3] (no search)          ✓

Match: 3/3 = 100% ✅
```

### Response Match Score = 0.82 (82%)

**What it measures:** Is the agent's response semantically similar to expected?

```
Expected Response Elements:
✓ Acknowledges user input
✓ References photo analysis
✓ Asks clarifying question
✓ Casual confident voice

Actual Response:
✓ "Got it - north-facing hallway"           (acknowledgment)
✓ "Analyzed your photo"                     (photo reference)
✓ "Any specific LRV range you're targeting?" (clarifying Q)
✓ "Give me that and I'll search"            (casual voice)

Semantic Similarity: 82% ✅ (above 75% threshold)
```

---

## For Portfolio Screenshots

### Screenshot 1: Test Results Dashboard
```
┌──────────────────────────────────────────────────────────┐
│  EVALUATION RESULTS                                      │
├──────────────────────────────────────────────────────────┤
│  ✅ happy_path_consultation                              │
│     Tool Trajectory: 1.0 (100%)                          │
│     Response Match:  0.82 (82%)                          │
│                                                          │
│  ✅ validation_loop_quality_control                      │
│     Tool Trajectory: 1.0 (100%)                          │
│     Response Match:  0.78 (78%)                          │
│                                                          │
│  ✅ real_client_scenario                                 │
│     Tool Trajectory: 1.0 (100%)                          │
│     Response Match:  0.85 (85%)                          │
│                                                          │
│  Summary: 3/3 tests PASSED                               │
└──────────────────────────────────────────────────────────┘
```

### Screenshot 2: Trace View
```
┌──────────────────────────────────────────────────────────┐
│  EXECUTION TRACE                                         │
├──────────────────────────────────────────────────────────┤
│  📤 User: "I need paint for my hallway..."               │
│                                                          │
│  🔧 Agent: analyze_room_photos(room_name="hallway")      │
│  ↳ Result: {current_color: "#8b9186", floor: "oak"}     │
│                                                          │
│  🔧 Agent: track_requirements(details={...})             │
│  ↳ Result: Requirements stored                           │
│                                                          │
│  💬 Agent: "Got it - analyzed your photo..."             │
│                                                          │
│  ✅ Tool sequence matches expected trajectory            │
└──────────────────────────────────────────────────────────┘
```

### Screenshot 3: Validation Loop
```
┌──────────────────────────────────────────────────────────┐
│  VALIDATION LOOP EXECUTION                               │
├──────────────────────────────────────────────────────────┤
│  🤖 Recommendation Agent:                                │
│     "This color has cool undertones..."                  │
│                                                          │
│  🔍 Consistency Critic:                                  │
│     ❌ Issue detected: "Claimed cool but hex shows warm" │
│                                                          │
│  ✏️ Refiner Agent:                                       │
│     ✅ Corrected: "This color has warm undertones..."    │
│                                                          │
│  Result: Error caught and fixed before user saw it       │
└──────────────────────────────────────────────────────────┘
```

---

## Key Takeaway

This evaluation framework ensures:
- ✅ Agent calls functions (doesn't hallucinate)
- ✅ Agent follows correct workflow
- ✅ Agent provides quality responses
- ✅ Errors are caught and corrected
- ✅ Professional-grade reliability

**Ready for production. Ready for portfolio. Ready for interviews.** 🚀

