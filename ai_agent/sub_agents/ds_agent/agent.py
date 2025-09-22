from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.agents.callback_context import CallbackContext
import os
from django.conf import settings
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)
from .prompts import get_ds_agent_instructions 
from .tools import holding_costs,setup_cost
from ai_agent.sub_agents.code_executor_tool.agent import code_executor_agent

AGENT_NAME = "ds_agent" 
APP_NAME = "Nina_Bazar"
GEMINI_MODEL = "gemini-2.0-flash"



ds_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    instruction=get_ds_agent_instructions(),
    tools=[agent_tool.AgentTool(agent=code_executor_agent),holding_costs,
           setup_cost
        ],
    

)

