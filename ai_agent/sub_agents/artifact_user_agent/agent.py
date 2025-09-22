from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService 
from google.adk.agents import LlmAgent
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types
from typing import Optional
from .tools import *
from google.adk.agents.callback_context import CallbackContext
import os
from django.conf import settings
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)

AGENT_NAME = "artifact_agent" 
APP_NAME = "Nina_Bazar"
GEMINI_MODEL = "gemini-2.0-flash"
USER_ID="user1234"
SESSION_ID="1234"

def my_before_model_logic(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print(f"Callback running before model call for agent: {callback_context.agent_name}")
    # ... your custom logic here ...
    return None # Allow the model call to proceed


artifact_agent =LlmAgent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    instruction="You are an expert in managing and saving artifacts. Your task is to save the provided report as an artifact in the system. Ensure that the artifact is saved correctly and provide a confirmation message with the artifact version once the operation is complete.",
    global_instruction="You are part of a team of agents working together to manage inventory and sales data for Nina Bazar. Today is {date_today}. Always ensure to follow your specific instructions carefully before responding.",
    tools=[generate_pdf],
    before_model_callback=my_before_model_logic
)


    
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=artifact_agent, app_name=APP_NAME, session_service=session_service,artifact_service=artifact_service)
    return session, runner




async def call_artifact_agent(data_bytes:bytes,mime_type:str) -> str:
    """ Calls the artifact agent to save a report as an artifact."""
    query = f"Created Python artifact from the provided data and save it using your tools. Confirm once saved."
    parts = [types.Part(text=query),types.Part(
    inline_data=types.Blob(
        mime_type=mime_type,
        data=data_bytes
    ))]
    content = types.Content(role='user', parts=parts)
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Artifact Agent Response: ", final_response)
            return final_response    
    return "No response from artifact agent"
    
 