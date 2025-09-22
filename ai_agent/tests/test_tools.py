"""Test cases for the analytics agent and its sub-agents."""
import pytest
from unittest.mock import patch,MagicMock
from ai_agent.sub_agents.db_agent.tools import execute_query, connect_to_db, get_table_info,get_tables
from ai_agent.sub_agents.artifact_user_agent.tools import save_generated_report
from ai_agent.sub_agents.ds_agent.tools import *
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
    expected =  {"status": "success", "lead_time":1}
    user = User.objects.create(id=233,password="bfhfjfj",last_login=datetime.datetime(2025, 9, 1,12, 26,49, 434555, tzinfo=datetime.timezone.utc))
    item = Item.objects.create(id=23232,name="test name ",description="test",price=decimal.Decimal('70.00'))
    receipt = Receipt.objects.create(id=1323,date=datetime.date(2025, 9, 1),bon_de_livraison=3234,qte_total=200,qte_by_carton=20,user_id=user.id)
    receipt_item = ReceiptItem.objects.create(id=23,description="test",quantity=23,unit_by_carton=10,cost_price=decimal.Decimal('70.00'),item_id=item.id,receipt_id= receipt.id)
    response = calculate_lead_time(item.id)
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
@pytest.mark.django_db(True)
def test_calculating_per_item_cost():
    user = User.objects.create(id=233,password="bfhfjfj",last_login=datetime.datetime(2025, 9, 1,12, 26,49, 434555, tzinfo=datetime.timezone.utc))
    item = Item.objects.create(id=22,name="test name ",description="test",price=decimal.Decimal('70.00'))
    receipt = Receipt.objects.create(id=1323,date=datetime.date(2025, 4, 3),bon_de_livraison=3234,qte_total=200,qte_by_carton=20,user_id=user.id)
    receipt_item = ReceiptItem.objects.create(id=23,description="test",quantity=23,unit_by_carton=10,cost_price=decimal.Decimal('70.00'),item_id=item.id,receipt_id= receipt.id)
    expected = 1643.8
    annual_storage_cost = 60000
    space_occupied = 1
    average_days_stored= calculate_lead_time(item.id,datetime.date(2025, 9, 23))
    response = calculating_per_item_cost(item.id,space_occupied)
    assert response == expected 





def test_average_cost_per_pallet():
    expected = 60.24
    response = average_cost_per_pallet()
    assert response == expected


def test_setup_cost():
    """The cost of placing an order"""
    expected = {'status':'success','setup_cost':1200}
    response = setup_cost()
    assert response == expected
    print(f"response:{response}")




@pytest.mark.django_db(True)
def test_holding_costs():
    """The cost of one pallet of inventory"""
    expected = {'status':'success','holdsing_cost':13.49}
    item = Item.objects.create(id=1,name="test name ",description="test",price=decimal.Decimal('77.98'))
    stock = Stock.objects.create(current_quantity=112,unit_by_carton=10,cost_price=decimal.Decimal('77.98'),item_id=item.id)
    response = holding_costs(item_id=item.id)
    assert response == expected
    print(f"response:{response}")


def test_EOQ():
    expected = 43.4
    response = eoq(13.49,100,127.05)
    print(f"EOQ={response}")
    assert response==expected
########################################################
#                                                      #
#             Test tools Artifact_user_agent           #
#                                                      #
# ######################################################    
#Note: Understanding artifacts involves grasping a few key components: the service that manages them
#the data structure used to hold them, and how they are identified and versioned.



@pytest.mark.asyncio
@patch('ai_agent.sub_agents.artifact_user_agent.tools.types')
@patch('ai_agent.sub_agents.artifact_user_agent.tools.ToolContext')
async def test_saving_generated_report(mock_tool_context,mock_types):
    """Test saving a generated report as an artifact."""
    filename = "generated_report.pdf"
    report_bytes = b'%PDF-1.7\n%\xc4\xe5\xf2\xe5\xeb\xa7\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n\n2 0 obj\n<<\n/Type /Pages\n/Kids [4 0 R]\n/Count 1\n>>\nendobj\n\n4 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 595 842]\n/Contents 5 0 R\n/Resources <<\n/ProcSet [/PDF /Text]\n/Font << /F1 6 0 R >>\n>>\n>>\nendobj\n\n5 0 obj\n<<\n/Length 55\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\n\n6 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/Name /F1\n/BaseFont /Helvetica\n>>\nendobj\n\nxref\n0 7\n0000000000 65535 f\n0000000009 00000 n\n0000000067 00000 n\n0000000122 00000 n\n0000000213 00000 n\n0000000262 00000 n\n0000000305 00000 n\n\ntrailer\n<<\n/Size 7\n/Root 1 0 R\n>>\nstartxref\n350\n%%EOF\n'
    mock_types = MagicMock()
    mock_tool_context = MagicMock()
    mock_content = MagicMock()
    mock_content.return_value = "This is a test report content."
    
    mock_types.Part.from_data(
        data=report_bytes,
        mime_type="application/pdf"
    )
    mock_types.Part.from_data.assert_called_with(
        data=report_bytes,
        mime_type="application/pdf"
    )

    report_artifact = mock_types.return_value()
    mock_tool_context.save_artifact(filename=filename, artifact=report_artifact)
    mock_tool_context.save_artifact.return_value = "artifact_version_123"
    mock_tool_context.save_artifact.assert_called_with(filename=filename, artifact=report_artifact)
    response = await save_generated_report(mock_tool_context, mock_content)
    assert response == {"status": "success", 'version': "artifact_version_123"}
   



@pytest.mark.asyncio
@patch('ai_agent.sub_agents.artifact_user_agent.tools.types')
@patch('ai_agent.sub_agents.artifact_user_agent.tools.ToolContext')
async def test_error_data_structure(mock_context,mock_types):
    """Test error handling when saving a generated report."""
    filename = "generated_report.pdf"
    report_bytes = b'\x89PNG\r\n\x1a\n...'
    mime_type = "application/pdf"
    mock_types = MagicMock()
    mock_context = MagicMock()
    
    mock_types.Part.from_data(
        data=report_bytes,
        mime_type=mime_type
    )
   

    report_artifact = mock_types.return_value()
    mock_context.save_artifact(filename=filename, artifact=report_artifact)
    mock_context.save_artifact.side_effect = ValueError("Simulated save error")
    response = await save_generated_report(report_bytes,mime_type,mock_context)
    print(f"response:{response}")
    assert response == {"status": "error", "error_message": "Invalid data structure provided for the artifact."}

@pytest.mark.asyncio
@patch('ai_agent.sub_agents.artifact_user_agent.tools.types')
@patch('ai_agent.sub_agents.artifact_user_agent.tools.ToolContext')
async def test_handling_error_exception(mock_context,mock_types):
    filename = "generated_report.pdf"
    report_bytes = b'\x89PNG\r\n\x1a\n...'
    mime_type = "application/pdf"
    mock_types = MagicMock()
    mock_types.Part.from_data(
        data=report_bytes,
        mime_type=mime_type
    )
   
    mock_context = MagicMock()
    
    mock_context.save_artifact.side_effect = Exception("Invalid mime_type")
    response = await save_generated_report(report_bytes,mime_type,mock_context)
    print(f"response:{response}")
    assert response == {"status": "error", "error_message": "Failed to save the artifact."} 

@pytest.mark.asyncio
@patch('ai_agent.sub_agents.artifact_user_agent.tools.types')
@patch('ai_agent.sub_agents.artifact_user_agent.tools.CallbackContext')
async def test_save_to_pdf_path():
    file_path = "test_report.pdf"