import matplotlib.pyplot as plt
import pandas as pd
import json
import tempfile
import datetime
from django.db.models import Max
from stock.models import ReceiptItem,Stock
date_today = datetime.date.today()
import decimal
from math import sqrt
import os 
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os
import base64

import asyncio
import logging # It's good practice to log errors

logger = logging.getLogger(__name__)

def calculate_lead_time(item_id:int,current_date=date_today)->dict:
    """Calculates the lead time for the stock item in days.
    Args:
        item_id: item_id.
        default_date: current_date.
    Returns:
        A dictionary with the lead time , e.g., {'status': 'success', 'result':53}

    """
    # current_date=date_today
    last_reorder= ReceiptItem.objects.filter(item_id=item_id).aggregate(Max('receipt__date'))['receipt__date__max']
    if last_reorder:
        lead_time = current_date - last_reorder
        return {"status": "success", f"lead_time": lead_time.days}
    else:
        return {'status': 'error'}


def get_purchase_price_of_goods()->dict:
    """
    the total value of the items currently in stock.
    """
    
    items = Stock.objects.all()
    result = decimal.Decimal(0.00)
    for i in items:
        cost = i.current_quantity * i.cost_price
        result += cost
    return {'status':'success','purchase_price_of_goods':result}    


def average_cost_per_pallet(total_monthly_waherhousing_costs=2000,number_of_pallet_space=83)->dict:
    """
    The Total warehousing costs divided by numer_of_space.
    """
    result = round((total_monthly_waherhousing_costs*12)/number_of_pallet_space,2)
    return result


def calculating_per_item_cost(item_id:int,space_occupied=1,annual_storage_cost=60000):
    """
    calculate the cost per item:
    Args:
        item_id = item ID

    """
    average_days_stored = calculate_lead_time(item_id,datetime.date(2025, 9, 23))
    avg_days = average_days_stored['lead_time']
    return round(avg_days*space_occupied*(annual_storage_cost/365),1)

def holding_costs(item_id:int)->dict:
    """The cost of one pallet of inventory"""   
    item = Stock.objects.get(item_id=item_id)
    pallet = 2.4
    quantity_item_per_pallet = (item.get_current_qte*0.001)/pallet
    average_cost = average_cost_per_pallet()
    result = round((average_cost*quantity_item_per_pallet),2)
    return {'status':'success','holdsing_cost':result}


def setup_cost():
    """Cost per order"""
    return {'status':'success','setup_cost':100.00}

def eoq(h,s,d):
    return round(sqrt((2*d*s)/h),2)




def save_artifact_data(filename: str, data_b64: str) -> None:
    """Saves base64-encoded binary data as a file."""
    data = base64.b64decode(data_b64)
    
    path = "/home/b-elbikam/Desktop/test_reports"
    file_path = os.path.join(path, filename)
    
    with open(file_path, "wb") as f:
        f.write(data)
    
    print(f"Artifact '{filename}' saved locally at {file_path}")




def generate_pdf_report(title: str, content: str) -> str:
    """
    Generates a PDF file from the given title and text content,
    encodes it in base64, and saves it via save_artifact_data.
    """
    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, title)
    c.setFont("Helvetica", 12)
    textobject = c.beginText(72, 725)
    textobject.textLines(content)
    c.drawText(textobject)
    c.save()
    
    pdf_bytes = buffer.getvalue()
    
    # Encode bytes to base64 string
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    
    # Define filename
    filename = f"{title.replace(' ', '_').lower()}.pdf"
    
    try:
        # Pass base64 string to save_artifact_data
        save_artifact_data(filename, pdf_b64)
        return f"PDF report '{filename}' generated and saved successfully."
    except Exception as e:
        return f"Error generating PDF: {e}"


import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import Dict, Any

async def generate_interactive_report(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a visual report based on the agent's provided data.
    Expected params format:
    {
        "chart_type": "bar" | "line" | "pie",
        "title": "Chart Title",
        "xlabel": "X axis",
        "ylabel": "Y axis",
        "data": {
            "x": [...],
            "y": [...],
            OR
            "labels": [...],
            "values": [...]
        }
    }
    """

    chart_type = params.get("chart_type", "bar").lower()
    data = params.get("data", {})

    if not data:
        return {
            "status": "error",
            "message": "Missing chart data."
        }

    plt.clf()

    try:
        if chart_type == "bar":
            plt.bar(data["x"], data["y"])
            plt.xlabel(params.get("xlabel", ""))
            plt.ylabel(params.get("ylabel", ""))
            plt.title(params.get("title", "Bar Chart"))

        elif chart_type == "line":
            plt.plot(data["x"], data["y"], marker='o')
            plt.xlabel(params.get("xlabel", ""))
            plt.ylabel(params.get("ylabel", ""))
            plt.title(params.get("title", "Line Chart"))

        elif chart_type == "pie":
            plt.pie(data["values"], labels=data["labels"], autopct='%1.1f%%')
            plt.title(params.get("title", "Pie Chart"))

        else:
            return {
                "status": "error",
                "message": f"Unsupported chart type '{chart_type}'."
            }

        # Convert the chart to base64 for return
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()

        return {
            "status": "success",
            "chart_type": chart_type,
            "image": f"data:image/png;base64,{img_base64}",
            "meta": {
                "title": params.get("title", ""),
                "xlabel": params.get("xlabel", ""),
                "ylabel": params.get("ylabel", "")
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating chart: {e}"
        }


async def get_report_data():
    summary = "Analysis business for year 2025"
    report_details = "This section contains the detailed findings for the annual business analysis."
    
    chart_data  = [['Task', 'Hours per Day'],
          ['Work',     7],
          ['Eat',      2],
          ['Commute',  2],
          ['Watch TV', 2],
          ['Sleep',   11]]

    # Define all your chart customizations here!
    # These names come directly from the Google Charts documentation.
    chart_options = {
        'title': 'My Daily Activities (Customized)',
        'is3D': False,
        'pieHole': 0.4, # This will make it a doughnut chart
        'colors': ["#1f88bc", '#e6693e', "#6d4089", "#1ba19b", "#0a2656"]
    }
    context = {
            'summary': summary,
            'report_details': report_details,
            'chart_data': chart_data,
            'chart_options': chart_options  # Add the options to the context
        }
    return context