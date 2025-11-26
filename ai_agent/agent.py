import asyncio
from abc import ABC,abstractmethod
import json
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner

from google.adk.sessions import InMemorySessionService, Session
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import RunConfig
from google.genai import types
from typing import Optional
import os
from django.conf import settings
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)
from .prompts import instructions_root_agent
from ai_agent.sub_agents.db_agent.agent import db_agent
from ai_agent.sub_agents.ds_agent.agent import ds_agent

import datetime 
date_today = datetime.datetime.today().strftime("%Y-%m-%d")

AGENT_NAME = "root_agent" 
APP_NAME = "Nina_Bazar"
USER_ID = "user12345"
SESSION_ID = "session_code_executors_async"
GEMINI_MODEL = "gemini-2.0-flash"






    
root_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    instruction=instructions_root_agent(),
    sub_agents=[db_agent,ds_agent],
    global_instruction=f"today is {date_today},please read carefily you instructions before to response ",
   
   

)




from abc import ABC,abstractmethod

class LLM(ABC):
    @abstractmethod
    async def setup_session_and_runner(self):
        pass
    @abstractmethod
    async def call_root_agent(self,query):
        pass
class GeminiAPI(LLM):
    async def setup_session_and_runner(self):
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        runner = Runner(agent=root_agent, app_name=APP_NAME,
                        session_service=session_service,artifact_service=artifact_service)
        
        return session, runner


    async def call_root_agent(self,query):
        content = types.Content(role='user', parts=[types.Part(text=query)])
        session, runner = await self.setup_session_and_runner()
        events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
        return events 
    
 