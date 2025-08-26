"""Test cases for the analytics agent and its sub-agents."""
import pytest
from unittest.mock import patch
from ai_agent.sub_agents.db_agent.tools import execute_query, connect_to_db, get_table_info,get_tables
from ai_agent.sub_agents.db_agent.agent import call_db_agent



@pytest.mark.asyncio
async def test_decide_tools():
    """Test the decision-making process of the agent."""
    expected_response = {"id": 1, "name": "Sample Item"}
    query = "What is the current quantity of item id=1 using tool execute_query?"

    response = call_db_agent("query")
    print(f"Response: {response}")
    assert response == expected_response


def test_execute_query():
    """Test the execute_query function."""
    expected_response = {'data': [{'SUM(quantity)': 677}], 'state': 'success'}
    query = "SELECT SUM(quantity) FROM sale_order_line;"
    response = execute_query(query)
    assert response == expected_response

def test_connect_to_db():
    """Test the database connection."""
    response = connect_to_db()
    assert response is not None


def test_get_tables():
    """Test the retrieval of table names from the database."""
    response = get_tables()
    assert response == [{"name":"django_migrations"},{"name":"sqlite_sequence"},{"name":"auth_group_permissions"},{"name":"auth_user_groups"},{"name":"auth_user_user_permissions"},{"name":"django_admin_log"},{"name":"django_content_type"},{"name":"auth_permission"},{"name":"auth_group"},{"name":"auth_user"},{"name":"stock_item"},{"name":"stock_the"},{"name":"stock_receipt"},{"name":"stock_receiptitem"},{"name":"stock_stockalert"},{"name":"sale_payment"},{"name":"sale_dealer"},{"name":"sale_sale"},{"name":"sale_cashpayment"},{"name":"sale_refunddealerpayment"},{"name":"sale_refundpayment"},{"name":"sale_devis"},{"name":"sale_devis_line"},{"name":"sale_refund"},{"name":"sale_saletopersone"},{"name":"sale_order_line"},{"name":"sale_salepayment"},{"name":"sale_monthlypayment"},{"name":"sale_refundnormal"},{"name":"sale_refund_line"},{"name":"sale_saletodealer"},{"name":"sale_refundfromdealer"},{"name":"django_session"},{"name":"stock_stock"}]


def test_get_table_info():
    """Test the retrieval of table information."""
    response = get_table_info('stock_stock')
    assert response == [{"name":"item_id"},{"name":"current_quantity"},{"name":"unit_by_carton"},{"name":"cost_price"},{"name":"lead_time"},{"name":"reorder_point"},{"name":"threshold_amount"}]