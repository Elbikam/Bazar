import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
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

ds_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description="This agent handles data science tasks.",
    instruction=get_ds_agent_instructions(),
    code_executor=BuiltInCodeExecutor()
)


session_service = InMemorySessionService()
session = asyncio.run(session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))

runner = Runner(agent=ds_agent, app_name=APP_NAME,
                session_service=session_service)

# In your ds_agent/agent.py file

async def call_ds_agent(query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n--- Running Query: {query} ---")
    
    # We will simply store the last text part we see.
    last_text_response = "No final text response captured." 
    
    try:
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            # This is your excellent debugging logic, keep it.
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.executable_code:
                        print(f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```")
                    elif part.code_execution_result:
                        print(f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}")
                    
                    # --- THE NEW LOGIC ---
                    # If we find a text part, we will update our variable.
                    # The last one we see before the loop ends will be the final answer.
                    elif part.text and part.text.strip():
                        current_text = part.text.strip()
                        print(f"  Text: '{current_text}'")
                        last_text_response = current_text

        # After the loop is completely finished, return the last text we captured.
        print(f"DS Agent Final Response: {last_text_response}")
        return last_text_response

    except Exception as e:
        print(f"ERROR during agent run: {e}")
        return None
    