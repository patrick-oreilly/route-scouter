from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from . import prompt
from dotenv import load_dotenv
import os

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


AGENT_NAME="google_search_agent"

GEMINI_MODEL="gemini-2.0-flash"
OPENAI_MODEL="gpt-4o-mini"

google_search_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description="Agent to search the web for running routes, locations and anything else",
    instruction=prompt.GOOGLE_SEARCH_AGENT_PROMPT,
    tools=[google_search],
)
