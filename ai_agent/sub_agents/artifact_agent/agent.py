from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService 
from google.genai.types import Image
import google.genai.types as types
from .tools import *
from google.adk.agents.callback_context import CallbackContext
import os
from django.conf import settings
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)
import asyncio
AGENT_NAME = "artifact_agent" 
APP_NAME = "Nina_Bazar"
GEMINI_MODEL = "gemini-2.0-flash"
USER_ID="user1234"
SESSION_ID="1234"



artifact_agent =LlmAgent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    # tools=[save_generated_report_pdf],
    # before_agent_callback= my_before_agent_callback
    

)
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=artifact_agent, app_name=APP_NAME,
                     session_service=session_service,artifact_service=artifact_service
                    )
    
    return runner




async def call_artifact_agent(query):
    """Calls the artifact agent to save a report as an artifact if the final response is text."""
    content = types.Content(role='user', parts=[types.Part(text=query)])
    runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
    artifact_service = InMemoryArtifactService()
    async for event in events:
        if event.content.parts and event.content.parts[0].text:
            print("  Type: Complete Text Message")
            if event.is_final_response():
                final_text = event.content.parts[0].text
                if isinstance(final_text, str): 
                    revision_id = await artifact_service.save_artifact(
                        app_name=APP_NAME,
                        user_id=USER_ID,
                        session_id=SESSION_ID,
                        filename="final_response.txt",  # Example filename
                        artifact=final_text
                    )
                    print("Final response saved as an artifact.")
                  
                else:
                    print("Final response is not text, skipping artifact save.")

   
            
        
        
        
        
    
           
    