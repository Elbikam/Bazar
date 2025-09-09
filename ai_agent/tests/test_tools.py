"""Test cases for the analytics agent and its sub-agents."""
import pytest
from unittest import mock 
from ai_agent.sub_agents.db_agent.tools import execute_query, connect_to_db, get_table_info,get_tables
import datetime
date_today = datetime.datetime.today().strftime("%Y-%m-%d")

def test_execute_query():
    """Test the execute_query function."""
    expected_response = {'data': [{'SUM(quantity)': 678}], 'state': 'success'}
    query = "select SUM(quantity) FROM sale_order_line;"

    response = execute_query(query)
    print(f"response:{response}")
    # assert response == expected_response

def test_connect_to_db():
    """Test the database connection."""
    response = connect_to_db()
    assert response is not None


def test_get_tables():
    """Test the retrieval of table names from the database."""
    response = get_tables()
    assert response == ['sale_sale', 'sale_saletopersone', 'sale_refund', 'sale_devis', 'sale_order_line', 'sale_devis_line', 'sale_refund_line', 'sale_dealer', 'sale_saletodealer', 'sale_refundfromdealer', 'sale_payment', 'sale_cashpayment', 'sale_monthlypayment', 'sale_refundpayment', 'sale_salepayment', 'sale_refunddealerpayment', 'sale_refundnormal', 'stock_item', 'stock_the', 'stock_stock', 'stock_receipt', 'stock_receiptitem', 'stock_stockalert', 'django_admin_log', 'auth_permission', 'auth_group', 'auth_user', 'django_content_type', 'django_session']

def test_get_table_info():
    """Test the retrieval of table information."""
    expected_res = ['item_id','current_quantity','unit_by_carton','cost_price','lead_time','reorder_point','threshold_amount']
    response = get_table_info('stock_stock')
    assert response == expected_res
    print(f"response:{response}")
    

    

