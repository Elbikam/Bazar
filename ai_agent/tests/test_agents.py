"""Test cases for the analytics agent and its sub-agents."""
from unittest import TestCase
import pytest
from ai_agent.sub_agents.db_agent.agent import call_db_agent
import datetime 
import asyncio




@pytest.mark.asyncio
async def test_call_db_agent():
    """"Test the db agent's call method."""
    print("\nWaiting for 60 seconds to respect API rate limits...")
    await asyncio.sleep(60)
    print("...continuing with test.")
    date = datetime.datetime.today().strftime("%Y-%m-%d")
    query = f"""
        You are a database agent that can answer questions about the Nina Bazar database.
        You can use SQL to query the database and return results in a human-readable format.
        You can also use the tools provided to interact with the database.using tools.
        You can use the following tools:
        1. `get_tables`: Use this tool to get to understand structure of database.
        2. `get_table_info`: Use this tool to get detailed information about a specific table, including its columns and data types.
        3. `execute_query`: Use this tool to run SQL queries on the database.
        
    today is {date}.what is total quantiy and value  purchase  of item LWADLAAER with id =1  this year"""
    response = await call_db_agent(query)
    print(f"DB Agent Response: {response}")



    