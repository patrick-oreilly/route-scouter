from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from . import prompt


google_search_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='google_search_agent',
    description="Searches the web for running routes, trails, and route planning resources",
    instruction=prompt.GOOGLE_SEARCH_AGENT_PROMPT,
    tools=[google_search],
)
