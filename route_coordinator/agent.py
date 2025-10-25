import os
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners import PlanReActPlanner
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from . import sub_agents
from . import prompt
import logging
import config

config.setup_logging()

logger = logging.getLogger(__name__)

load_dotenv()

AGENT_NAME="route_coordinator"

location_scout = sub_agents.location_scout.location_scout
route_builder = sub_agents.route_builder.route_builder
elevation_analyst = sub_agents.elevation_analyst.elevation_analyst



workflow = SequentialAgent(
    name="route_workflow",
    sub_agents=[location_scout, route_builder, elevation_analyst],
    description="A workflow that scoutes a given location, then plots a running route and after that analises its elevation",
)



route_coordinator = LlmAgent(
    name=AGENT_NAME,
    model=LiteLlm(model=os.getenv("OPENAI_MODEL","GROK_MODEL")),
    tools=[AgentTool(agent=workflow)],
    description="Coordinates running route scouting.",
    instruction=prompt.ROUTE_COORDINATOR_PROMPT,
)