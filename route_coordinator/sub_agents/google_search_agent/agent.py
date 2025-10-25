from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search
from . import prompt
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_NAME="google_search_agent"

google_search_agent = LlmAgent(
    model="gemini-2.0-flash",
    name=AGENT_NAME,
    description="Agent to search the web for running routes, locations and anything else",
    instruction=prompt.GOOGLE_SEARCH_AGENT_PROMPT,
    output_key="google_search_results",
    tools=[google_search],
)
