from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types
import os
from django.conf import settings
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)
from .prompts import get_ds_agent_instructions 

AGENT_NAME = "ds_agent" 
APP_NAME = "Nina_Bazar"
USER_ID = "user12345"
SESSION_ID = "session_code_executors_async"
GEMINI_MODEL = "gemini-2.0-flash"
# GEMINI_MODEL = 'gemini-1.5-pro-latest'

ds_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    instruction=get_ds_agent_instructions(),
    code_executor=BuiltInCodeExecutor()
)

    