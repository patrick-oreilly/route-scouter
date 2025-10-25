import os
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners import PlanReActPlanner
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from . import sub_agents
from . import prompt

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

location_scout = sub_agents.location_scout.location_scout
google_search_agent = sub_agents.google_search_agent.google_search_agent
route_builder = sub_agents.route_builder.route_builder
elevation_analyst = sub_agents.elevation_analyst.elevation_analyst


AGENT_NAME="route_coordinator"
GEMINI_MODEL="gemini-2.0-flash"
OPENAI_MODEL= LiteLlm(model="openai/gpt-4.1")
GROK_MODEL = LiteLlm(model="xai/grok-3-mini-beta")
MISTRAL_MODEL = LiteLlm(model="ollama_chat/mistral:7b")



route_coordinator = LlmAgent(
    name=AGENT_NAME,
    model=OPENAI_MODEL,
    tools=[
        AgentTool(agent=location_scout),
        AgentTool(agent=google_search_agent),
        AgentTool(agent=route_builder),
        AgentTool(agent=elevation_analyst),
           ],
    description="Coordinates running route scouting.",
    instruction=prompt.ROUTE_COORDINATOR_PROMPT,
)