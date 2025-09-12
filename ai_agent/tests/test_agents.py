"""Test cases for the analytics agent and its sub-agents."""
from unittest import TestCase,mock
import pytest
from ai_agent.agent import call_root_agent
import asyncio



@pytest.mark.asyncio
async def test_quantity_sold_it():
    query = "what is total quantity sold it for month July 2025?"
    expected_response = "The total quantity sold in July 2025 is 155."
    response = await call_root_agent(query)
    # assert response == expected_response

@pytest.mark.asyncio
async def test_calculate_total_sales():
    q="What is total sales for this year 2025?"  
    response = await call_root_agent(q) 
    print(f"response:{response}")
    # assert response == "The total sales for the year 2025 is 63680.8."

@pytest.mark.asyncio
async def test_current_qte_and_value():
    query = "what is total current quantity in the stock and value?"
    response = await call_root_agent(query)
    


@pytest.mark.asyncio
async def test_pareto_chart():
    query = "Please generate Pareto chart"
    response = await call_root_agent(query)
    print(f"response:{response}")

@pytest.mark.asyncio
async def test_20_80():
    query = "i want to find the items (name and ID) that contribute to 80% of total revenue?"
    response = await call_root_agent(query)
    
    print(f"response:{response}")

@pytest.mark.asyncio
async def test_give_smart_rec():
    query = "could you give me smart recommondations what can i purchasse for this month and what can reduce from stock?"  
    response = await call_root_agent(query) 

@pytest.mark.asyncio
async def test_forcasting():
    query = "Create a sales forecast."\
    "product forcasting all items"\
    "period:next week"\
    "factors:sales"
    response = await call_root_agent(query)
@pytest.mark.asyncio
async def test_summary_analysis():
    query = "give me summary analysis for this year 2025"
    response = await call_root_agent(query)

@pytest.mark.asyncio
async def test_calculate_total_for_each_item():
    query = "what is total sales for each items for this year?"
    response = await call_root_agent(query)
@pytest.mark.asyncio
async def test_item_not_existe():
    query = "what is current quantity of item X with id=232 ?" 
    response = await call_root_agent(query)   
@pytest.mark.asyncio
async def test_calculate_optimal_stock():
    q="Calcule the optiomal stock for each item.what are the tools to acheive this goal,also how ?"
    response = await call_root_agent(q)
