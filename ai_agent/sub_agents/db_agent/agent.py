from google.adk.agents import LlmAgent
from .tools import execute_query
from .prompts  import db_instruction_prompt
import logging
logger = logging.getLogger(__name__)
import os
from django.conf import settings

os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)


AGENT_NAME = "db_agent"
APP_NAME = "Nina_Bazar"
USER_ID = "user1234"
SESSION_ID = "session_execeute_query_async"
GEMINI_MODEL = "gemini-2.0-flash"



db_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    instruction=db_instruction_prompt(),
    tools=[execute_query],
    

)



