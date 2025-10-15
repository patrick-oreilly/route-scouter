import os
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners import PlanReActPlanner
from . import sub_agents
from . import prompt

location_scout = sub_agents.location_scout.location_scout
google_search_agent = sub_agents.google_search_agent.google_search_agent
route_builder = sub_agents.route_builder.route_builder
elevation_analyst = sub_agents.elevation_analyst.elevation_analyst


information_gathering = ParallelAgent(
            name="information_gathering",
            sub_agents=[location_scout, google_search_agent],
            description="A parallel agent that gathers location information and answers questions using Google Search.",
        )
workflow = SequentialAgent(
    name="route_scouting_workflow",
    sub_agents=[information_gathering, route_builder, elevation_analyst],
    description="A sequential agent that coordinates the route scouting process by first gathering information, then building the route, and finally analyzing elevation.",
)

route_coordinator = LlmAgent(
    name="route_coordinator",
    model="gemini-2.0-flash",
    tools=[AgentTool(agent=workflow)],
    description="Coordinates running route scouting.",
    instruction=prompt.ROUTE_COORDINATOR_PROMPT,
)