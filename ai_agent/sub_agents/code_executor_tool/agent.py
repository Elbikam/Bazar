from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor
from .prompt import get_instructions
import os
from django.conf import settings
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)


AGENT_NAME = "code_executor_agent" 
APP_NAME = "Nina_Bazar"
GEMINI_MODEL = "gemini-2.0-flash"


code_executor_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    instruction=get_instructions(),
    code_executor=BuiltInCodeExecutor()
)
