import os
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from . import sub_agents
from . import prompt

root_agent = LlmAgent(
    name="route_coordinator",
    model="gemini-2.0-flash-thinking-exp",
    description=(
        "Coordinates running route scouting by orchastrating a series of expert subagents."
      ),
    instruction=prompt.ROUTE_COORDINATOR_PROMPT,

    tools=[
        AgentTool(agent=sub_agents.location_scout.location_scout),
        AgentTool(agent=sub_agents.route_builder.route_builder),
        AgentTool(agent=sub_agents.elevation_analyst.elevation_analyst),
    ]
)