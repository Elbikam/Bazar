"""Test cases for the analytics agent and its sub-agents."""
from unittest import TestCase
import pytest
from ai_agent.sub_agents.db_agent.agent import call_db_agent
from ai_agent.sub_agents.ds_agent.agent import call_ds_agent
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
   who are the top 5 customers by total sales this year 2025?"""
    response = await call_db_agent(query)
    print(f"DB Agent Response: {response}")



@pytest.mark.asyncio
async def test_call_ds_agent():
    """"Test the data science agent's call method."""
    print("\nWaiting for 60 seconds to respect API rate limits...")
    await asyncio.sleep(60)
    print("...continuing with test.")
    query = """ Calculate the value of (5 + 70) * 3 """
    response  = await call_ds_agent(query)
    print(f"DS Agent Response: {response}")