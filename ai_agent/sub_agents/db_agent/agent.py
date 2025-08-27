import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.agents import LlmAgent, BaseAgent
from .tools import execute_query, connect_to_db,get_tables,get_table_info
from .prompts  import get_db_agent_instruction
import logging
logger = logging.getLogger(__name__)
import uuid
import os
from django.conf import settings
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.genai import types

os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)

AGENT_NAME = "db_agent "
APP_NAME = "Nina_Bazar"
USER_ID = "user1234"
SESSION_ID = "session_execeute_query_async"
GEMINI_MODEL = "gemini-2.0-flash"


db_agent = LlmAgent(
    model=GEMINI_MODEL,
    name=APP_NAME,
    description="This agent handles database queries.",
    instruction=get_db_agent_instruction(),
    tools=[execute_query, connect_to_db, get_tables, get_table_info ],
)

session_service = InMemorySessionService()
session = asyncio.run(session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))

runner = Runner(agent=db_agent, app_name=APP_NAME,
                session_service=session_service)

async def call_db_agent(query):
    """Calls the database agent with a natural language query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n--- Running Query: {query} ---")
    final_response_text = "No final text response captured."
    try:
        async for response_event in runner.run_async(new_message=content, session_id=SESSION_ID, user_id=USER_ID):
            # Check for content directly within the Event object
            if hasattr(response_event, 'content') and response_event.content and response_event.content.parts:
                for part in response_event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(f"Agent Response Part: {part.text}")
                        final_response_text = part.text
            # Check for tool calls directly within the Event object
            elif hasattr(response_event, 'tool_calls') and response_event.tool_calls:
                for tool_call in response_event.tool_calls:
                    print(f"Tool Call: {tool_call.tool_name} with args {tool_call.arguments}")
            else:
                # This else block can be removed once you're confident all types are handled
                print(f"Unhandled response event type or structure: {response_event}")

        return final_response_text
    except Exception as e:
        print(f"ERROR during agent run: {e}")
        return f"Error: {e}" # Return error message to avoid None
    finally: # Ensures the separator is always printed
        print("-" * 30)

