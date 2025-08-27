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
 today is {date}.what is total sales for month June 2025"""
    response = await call_db_agent(query)
    print(f"DB Agent Response: {response}")



    