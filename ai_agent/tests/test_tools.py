"""Test cases for the analytics agent and its sub-agents."""
import pytest
from unittest.mock import patch,MagicMock
from ai_agent.sub_agents.db_agent.tools import execute_query, connect_to_db, get_table_info,get_tables
from ai_agent.sub_agents.ds_agent.tools import calculate_lead_time,get_purchase_price_of_goods
import datetime
import decimal
from stock.models import *
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





@pytest.mark.django_db(True)
def test_calculate_lead_time():
    expected =  {"status": "success", "lead_time":11 }
    user = User.objects.create(id=233,password="bfhfjfj",last_login=datetime.datetime(2025, 9, 1,12, 26,49, 434555, tzinfo=datetime.timezone.utc))
    item = Item.objects.create(id=22,name="test name ",description="test",price=decimal.Decimal('70.00'))
    receipt = Receipt.objects.create(id=1323,date=datetime.date(2025, 4, 3),bon_de_livraison=3234,qte_total=200,qte_by_carton=20,user_id=user.id)
    receipt_item = ReceiptItem.objects.create(id=23,description="test",quantity=23,unit_by_carton=10,cost_price=decimal.Decimal('70.00'),item_id=item.id,receipt_id= receipt.id)
    response = calculate_lead_time(item.id,datetime.date(2025, 9, 23))
    assert response == expected
    print(f"response:{response}")


@pytest.mark.django_db(True)
def test_get_purchase_price_of_goods():
    item = Item.objects.create(id=22,name="test name ",description="test",price=decimal.Decimal('70.00'))
    stock = Stock.objects.create(current_quantity=23,unit_by_carton=10,cost_price=decimal.Decimal('70.00'),item_id=item.id)
    response = get_purchase_price_of_goods()
    assert response == {'status':'success','purchase_price_of_goods':Decimal('1610.00')}


def test_inventory_service_costs():
    pass
def test_storage_space_costs():
    pass
def test_inventory_risk_costs():
    pass
def test_holding_costs():
    pass