from typing import List
import os

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from .tools import (
    query_catalog, estimate_lighting, export_schedule,
    validate_schedule, ingest_catalog_csv,
    search_colors_smart, analyze_room_photos,
    track_requirements, validate_against_requirements
)
from ..browser_automation.browser_agent_tool import order_paint_samples
from .prompt import get_composed_instruction, get_critic_instruction, get_refiner_instruction

# Model selection - using latest and most capable model (April 2025)
MODEL_DEFAULT = "gemini-2.5-pro"
MODEL = os.getenv("MODEL", MODEL_DEFAULT)

# Exit loop tool for validation loop
def exit_loop(tool_context: ToolContext):
    """
    Call this function ONLY when the critique indicates no further changes are needed,
    signaling the validation loop should end.
    """
    print(f"[Validation Complete] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}

# Create tools
query_catalog_tool = FunctionTool(query_catalog)
search_colors_smart_tool = FunctionTool(search_colors_smart)
estimate_lighting_tool = FunctionTool(estimate_lighting)
analyze_room_photos_tool = FunctionTool(analyze_room_photos)
export_schedule_tool = FunctionTool(export_schedule)
validate_schedule_tool = FunctionTool(validate_schedule)
ingest_catalog_csv_tool = FunctionTool(ingest_catalog_csv)
track_requirements_tool = FunctionTool(track_requirements)
validate_against_requirements_tool = FunctionTool(validate_against_requirements)
order_paint_samples_tool = FunctionTool(order_paint_samples)
exit_loop_tool = FunctionTool(exit_loop)

# Main recommendation agent
recommendation_agent = LlmAgent(
    model=MODEL,
    include_contents='default',  # Needs conversation history for multi-turn consultation
    name="color_recommender",
    tools=[
        query_catalog_tool,
        search_colors_smart_tool,
        estimate_lighting_tool,
        analyze_room_photos_tool,
        export_schedule_tool,
        validate_schedule_tool,
        ingest_catalog_csv_tool,
        track_requirements_tool,
        validate_against_requirements_tool,
        order_paint_samples_tool,
    ],
    instruction=get_composed_instruction(),
    output_key="recommendation"
)

# Consistency validation critic
consistency_critic = LlmAgent(
    model=MODEL,
    include_contents='none',  # Clean state management
    name="consistency_critic",
    instruction=get_critic_instruction(),
    output_key="criticism"
)

# Refiner that fixes issues or exits loop
refiner = LlmAgent(
    model=MODEL,
    include_contents='default',  # Needs conversation history to understand phase
    name="refiner",
    tools=[exit_loop_tool],
    instruction=get_refiner_instruction(),
    output_key="recommendation"
)

# Validation loop (critic → refiner until consistent)
validation_loop = LoopAgent(
    name="validation_loop",
    sub_agents=[consistency_critic, refiner],
    max_iterations=3  # Prevent infinite loops
)

# Restore validation loop - it validates recommendations after agent completes them
# The loop only runs after agent makes color recommendations, not during Q&A
root_agent = SequentialAgent(
    name="color_flow_paint_agent",
    sub_agents=[
        recommendation_agent,
        validation_loop
    ]
)
