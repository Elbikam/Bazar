"""Test cases for the analytics agent and its sub-agents."""
from unittest.mock import patch,MagicMock
import pytest
from ai_agent.agent import call_root_agent
from ai_agent.sub_agents.artifact_user_agent.agent import *
import asyncio



@pytest.mark.asyncio
async def test_quantity_sold_it():
    query = "what is total quantity sold it for month July 2025?"
    expected_response = "The total quantity sold in July 2025 is 155."
    response = await call_root_agent(query)


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



@pytest.mark.asyncio
async def test_calculate_EOQ():
    q="calculating the Economic Order Quantity (EOQ) for each items in stock.to fetch data use db_agent and to analysis use ds_agent."\
    "the annual demand for each item based on the available sales data"\
    "Use tools Holding cost setup_cost to get info "
    response = await call_root_agent(q)
  

##############################################
#         TEST Artifact AGENT                #                                   
#                                            #
##############################################

@pytest.mark.asyncio
async def test_pdf_artifact():
    """ Test generating and saving a PDF artifact. Hello World PDF"""
    pdf_bytes = b'%PDF-1.7\n%\xc4\xe5\xf2\xe5\xeb\xa7\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n\n2 0 obj\n<<\n/Type /Pages\n/Kids [4 0 R]\n/Count 1\n>>\nendobj\n\n4 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 595 842]\n/Contents 5 0 R\n/Resources <<\n/ProcSet [/PDF /Text]\n/Font << /F1 6 0 R >>\n>>\n>>\nendobj\n\n5 0 obj\n<<\n/Length 55\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\n\n6 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/Name /F1\n/BaseFont /Helvetica\n>>\nendobj\n\nxref\n0 7\n0000000000 65535 f\n0000000009 00000 n\n0000000067 00000 n\n0000000122 00000 n\n0000000213 00000 n\n0000000262 00000 n\n0000000305 00000 n\n\ntrailer\n<<\n/Size 7\n/Root 1 0 R\n>>\nstartxref\n350\n%%EOF\n'
    mime_type = "application/pdf"           
    response = await call_artifact_agent(pdf_bytes, mime_type)
    assert "The PDF has been generated and saved as 'generated_report.pdf' with version '0'" in response
    print(f"response:{response}")
   
    
    

@pytest.mark.asyncio
async def test_image_artifact():
    image_bytes = b'\x89PNG\r\n\x1a\n...' # Your raw image data
    image_mime_type = "image/png"           
    response = await call_artifact_agent(image_bytes, image_mime_type)
    # assert response == "artifact_version_123"
    print(f"response:{response}")
