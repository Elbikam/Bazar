# dashboard/reporting.py
from stock.models import *
from sale.models import *
from django.db.models import Sum
from datetime import datetime
import plotly.graph_objects as go
from django.http import JsonResponse
from decimal import Decimal
import pandas as pd
import plotly.express as px
import os
from django.conf import settings
from django.db.models import Max

import matplotlib.pyplot as plt
#//////////////////////////////////////////////////////////////////
def get_inventory_summary_data():
    """Retrieves a summary of the current inventory (returns raw data)."""
    stocks = Stock.objects.all()
    inventory_data = []
    for stock in stocks:
        item_data = {
            'item_id': stock.item.id, #Change
            'product_name': stock.item.name, #Change
            'description': stock.item.description,  # Access description through stock.item
            'stock quantity': stock.current_quantity, #Change
            'threshold_amount':stock.threshold_amount, #Change
            'unit_by_carton':stock.unit_by_carton, #Change
            'selling_price': float(stock.item.price),  # Ensure price is a float #Change
            'cost_price': float(stock.cost_price),  # Ensure cost_price is a float #Change
            'lead_time': stock.lead_time,#Change
            'reorder_point': stock.reorder_point,#Change

        }
        inventory_data.append(item_data)
    return inventory_data    
   


def get_sales_data(date=None,category=None):
    """Retrieves a sales data"""
    if date is None:
        date = datetime.now()  # Default to current date

    # Extract year and month from the date
    year = date.year
    month = date.month

    # Filter sales based on the specified month and year
    sales = Order_Line.objects.filter(sale__date__year=year, sale__date__month=month).all()
    sales_data = []
    for s in sales:
        order_data={
            'date':s.sale.date.strftime('%Y-%m-%d'),
            'item_id':s.item_id,
            'item name':s.item.item.name,
            'quantity':s.quantity,
            'price selling': float(s.price) if isinstance(s.price, Decimal) else s.price,
            'price cost': float(s.item.cost_price) if isinstance(s.item.cost_price, Decimal) else s.item.cost_price

        }
        sales_data.append(order_data)

    return {
        'sales data':sales_data,
    }

def get_refunds_data(date=None):
    """Retrieves a refunds data."""
    if date is None:
        date = datetime.now()  # Default to current date

    year = date.year
    month = date.month

    # Filter refunds based on the specified month and year
    refunds = Refund_Line.objects.filter(refund__date__year=year, refund__date__month=month).all()
    refunds_data = []
    for r in refunds:
        refund_data={
            'refund_date':r.refund.date.strftime('%Y-%m-%d'),
            'item_refund_id':r.item_id,
            'item refund name':r.item.item.name,
            'reason refund':r.refund.reason,
            'quantity ':r.quantity,
            'price selling ': float(r.price) if isinstance(r.price, Decimal) else r.price,
            'price cost': float(r.item.cost_price) if isinstance(r.item.cost_price, Decimal) else r.item.cost_price,
        }
        refunds_data.append(refund_data)
    return {
        'refunds data': refunds_data
    }
#tools:The inventory Report
def get_the_data():
    """Retrieves the current stock information for items belonging to a specific subclass,
      referred to as 'The'. This includes details such as item ID, name, description, price, reference, and weight. The function 
    filters the inventory to return only those items that are categorized under 
    the specified subclass."""
    inventory = Stock.objects.all()
    the_in_inventory=[]
    for t in inventory:
        if t.item.the:
            t={
                'id':t.pk,
                'name':t.item.name,
                'description':t.item.description,
                'current_quantity':t.current_quantity,
                'price':float(t.cost_price)if isinstance(t.cost_price, Decimal) else t.cost_price,
                'ref':t.item.the.ref,
                'weight':t.item.the.weight

            }
            the_in_inventory.append(t)

    return {
        'the_in_inventory':the_in_inventory  }  
#tools:History Purchassing 
def get_the_purchass_data():
    receipt_items = ReceiptItem.objects.all()
    the_purchassing = []
    for r in receipt_items:
        if r.item.the:
            r={
                'date':r.receipt.date.strftime('%Y-%m-%d'),
                'receipt_id':r.id,
                'item_id':r.item.id,
                'item name':r.item.name,
                'quantity PurchaseOrder':r.quantity,
                'cost_price':float(r.cost_price) if  isinstance(r.cost_price, Decimal) else r.cost_price,
            }
            the_purchassing.append(r)
    return {
        'the purchass Order':the_purchassing}
       
#tolls:The sales data
def get_the_sales_data(date=None):
    if date is None:
        date = datetime.now()
    year = date.year
    month = date.month
    sales = Order_Line.objects.filter(sale__date__year=year, sale__date__month=month).all()
    the_sales_data = []
    for s in sales:
        if s.item.item.the:
            order_data={
                'date':s.sale.date.strftime('%Y-%m-%d'),
                'item_id':s.item.pk,
                'item name':s.item.item.name,
                'quantity':s.quantity,
                'price selling': float(s.price) if isinstance(s.price, Decimal) else s.price,
                'price cost': float(s.item.cost_price) if isinstance(s.item.cost_price, Decimal) else s.item.cost_price,
                'ref':s.item.item.the.ref,
                'weight':s.item.item.the.weight}
            the_sales_data.append(order_data)
    return {
        'the_sales data':the_sales_data,
    }

#tool LEAD TIME
def get_lead_time():
    """Retreive lead time for each items ins stock """
    s=Stock.objects.all()
    lead_time = []
    for i in s:
        item = {
            'item_id':i.pk,
            'item name':i.item.name,
            'current quantity':i.current_quantity,
            'lead time':i.calculate_lead_time(),
        }
        lead_time.append(item)
    return {
        'lead_time':lead_time
    } 
#list The data 
def get_the_sales_data_asList(date=None):
    if date is None:
        date = datetime.now()
    year = date.year
    month = date.month
    sales = Order_Line.objects.filter(sale__date__year=year, sale__date__month=month).all()
    the_sales_data = []
    for s in sales:
        if s.item.item.the:
            order_data={
                'date':s.sale.date.strftime('%Y-%m-%d'),
                'item_id':s.item.pk,
                'item name':s.item.item.name,
                'quantity':s.quantity,
                'price selling': float(s.price) if isinstance(s.price, Decimal) else s.price,
                'price cost': float(s.item.cost_price) if isinstance(s.item.cost_price, Decimal) else s.item.cost_price,
                'ref':s.item.item.the.ref,
                'weight':s.item.item.the.weight}
            the_sales_data.append(order_data)
    return the_sales_data
    
#tool gerenerate sales qte bar chart
def generate_sales_quantity_bar_chart(monthly_sales_data):
    """Generates a bar chart for sales quantities."""
    if not monthly_sales_data:
        print("No sales data provided for the chart.")
        return None

    # Convert list of sales data dictionaries to DataFrame
    df = pd.DataFrame(monthly_sales_data)

    # Group by item_id and item name, then sum the quantities
    sales_summary = df.groupby(['item_id', 'item name'])['quantity'].sum().reset_index()

    # Create the bar chart using Plotly
    fig = px.bar(sales_summary, x='item name', y='quantity',
                 color='item_id',  # Use item_id for color differentiation
                 labels={'quantity': 'Total Quantity Sold', 'item name': 'Item'},
                 title='Sales Quantity Bar Chart')

    # Update layout for better visualization
    fig.update_layout(
        xaxis_title="Item",
        yaxis_title="Total Quantity Sold",
        title_x=0.5,  # Center title
        barmode='group'  # Group bars by item_id
    )

    # Define save path (use a distinct name)
    chart_filename = 'sales_quantity_bar_chart.html'  # Save as HTML for better compatibility
    chart_save_path = os.path.join(settings.STATICFILES_DIRS[0], chart_filename)
    fig.write_html(chart_save_path)

    # Define static URL path for the HTML file
    chart_url_path = f"/static/{chart_filename}"
    print(f"Generated Sales Quantity Bar Chart: {chart_url_path}")  # Debugging
    return chart_url_path





##//////////////////////////////////////////////////////////////////////////////////////////////////////////
def generate_sales_quantity_bar_chart(data: list):
    """
    Generates a bar chart showing the quantity sold for each item in a specified subclass ("The" or "Parfum").
    (Uses Matplotlib)
    """

    sales_data = {}
    for i in data:  # data is list of dictionaries
        if i['item_id'] in sales_data.keys():
            sales_data[i['item_id']] += i['quantity']  # Update quantity
        else:
            sales_data[i['item_id']] = i['quantity']  # Initialize quantity

    if not sales_data:
        return "No sales data found for subclass."

    # Convert sales_data to a DataFrame for better handling
    df = pd.DataFrame(list(sales_data.items()), columns=['item_id', 'quantity'])

    # Create the bar chart using Plotly instead of Matplotlib
    fig = px.bar(df, x='item_id', y='quantity',
                 labels={'quantity': 'Total Quantity Sold', 'item_id': 'Item ID'},
                 title='Sales Quantity Bar Chart')

    # Update layout for better visualization
    fig.update_layout(
        xaxis_title="Item ID",
        yaxis_title="Total Quantity Sold",
        title_x=0.5  # Center title
    )

    # Define save path (use a distinct name)
    chart_filename = 'sales_quantity_bar_chart.html'
    chart_save_path = os.path.join(settings.STATICFILES_DIRS[0], chart_filename)
    fig.write_html(chart_save_path)

    # Define static URL path for the HTML file
    chart_url_path = f"/static/{chart_filename}"
    print(f"Generated Sales Quantity Bar Chart: {chart_url_path}")  # Debugging
    return chart_url_path


















# ----------------------------------------------------------------------------------------

def generate_stock_level_vs_sales_chart(data: list) -> str:
    """
    Generates a combined chart showing both the current stock level and the sales quantity for each item.

    Args:
        data (list): A list of Stock dictionaries, where each stock dictionary has 'stock_level' and sales data derived from ReceiptItems.
                     The structure is as follows:
                     [
                         {
                            'item': {
                                  'id': int,
                                  'name': str,
                                   'description': str,
                                   'current_quantity': int
                                },
                             'stock_level': int,  # Current stock level
                             'total_quantity_sold': int  # Total quantity sold
                         },
                         ...
                     ]

    Returns:
        str: A string representation of the combined chart.
    """

    if not data:
        return "No data available to generate the stock level vs. sales chart."

    # Logic to generate the combined chart (replace with your preferred charting library)
    chart_string = "Stock Level vs. Sales Quantity:\n"
    for item_data in data:
        chart_string += f"{item_data['item']['name']}: Stock = {item_data['stock_level']}, Sales = {item_data['total_quantity_sold']}\n"

    return chart_string
#////////////////////////////////////////////////////////////////////////////////////////////////////////////


















def generate_monthly_sales_pareto(monthly_sales_data):
    """
    Generates a Pareto chart from a list of monthly sales data dictionaries
    and saves it to a static file.

    Args:
        monthly_sales_data (list): A list of dictionaries, where each dict
                                   represents an order line like:
                                   {'item name': str, 'quantity': int, 'price selling': float}

    Returns:
        str: The static URL path to the generated chart HTML file, or None if no data.
    """
    if not monthly_sales_data:
        return None

    # Convert list of dicts to DataFrame
    df = pd.DataFrame(monthly_sales_data)

    # Calculate total sales value per item
    df['total_value'] = df['quantity'] * df['price selling']
    sales_by_item = df.groupby('item name')['total_value'].sum().reset_index()

    # Sort by sales value descending
    df_sorted = sales_by_item.sort_values(by='total_value', ascending=False)

    # Calculate cumulative percentage
    total_sales = df_sorted['total_value'].sum()
    if total_sales == 0: # Avoid division by zero if no sales
        return None
    df_sorted['cumulativePercentage'] = (df_sorted['total_value'].cumsum() / total_sales) * 100

    # Create the Pareto chart using Plotly
    fig = px.bar(df_sorted, x='item name', y='total_value',
                 labels={'total_value': 'Sales Value (Current Month)', 'item name': 'Item'},
                 title='Monthly Sales Pareto Chart')

    fig.add_trace(go.Scatter(x=df_sorted['item name'], y=df_sorted['cumulativePercentage'],
                             mode='lines+markers', name='Cumulative %', yaxis="y2"))

    fig.update_layout(
        yaxis_title="Sales Value",
        yaxis2=dict(
            title='Cumulative Percentage',
            overlaying='y',
            side='right',
            range=[0, 105], # Extend range slightly
            showgrid=False
        ),
        title_x=0.5 # Center title
    )

    # Define save path (use a distinct name)
    chart_filename = 'monthly_pareto_chart.html'
    chart_save_path = os.path.join(settings.STATICFILES_DIRS[0], chart_filename)
    fig.write_html(chart_save_path)

    # Define static URL path
    chart_url_path = f"/static/{chart_filename}"
    print(f"Generated Pareto chart: {chart_url_path}") # Debugging
    return chart_url_path

def get_most_sales_product():
    """
    Generates a Pareto chart of ALL product sales and saves it to a static file.
    Returns the path to the saved chart.
    """
    from sale.models import Order_Line #Import here to avoid top circular depedency

    # Calculate the data for the Pareto chart
    order_lines = Order_Line.objects.all().select_related('item__item')
    sales_by_item = {}
    for ol in order_lines:
        # Ensure item and item.item exist before accessing id/name
        if ol.item and ol.item.item:
            item_id = ol.item.item.id
            item_name = ol.item.item.name # Get name here
            sales_value = ol.quantity * float(ol.price) # Use float price
            if item_name not in sales_by_item:
                 sales_by_item[item_name] = 0
            sales_by_item[item_name] += sales_value
        else:
            print(f"Warning: Skipping Order_Line {ol.id} due to missing item link.")


    # Convert sales_by_item data to a DataFrame
    if not sales_by_item:
         print("Warning: No sales data found for Pareto chart.")
         return None # Handle case with no sales

    df = pd.DataFrame(list(sales_by_item.items()), columns=['item_name', 'sales'])
    df = df.sort_values(by='sales', ascending=False)

    # Calculate cumulative percentage
    total = df['sales'].sum()
    if total == 0:
        print("Warning: Total sales are zero for Pareto chart.")
        return None # Handle zero total sales

    df['cumulativePercentage'] = (df['sales'].cumsum() / total) * 100

    # Create the Pareto chart using Plotly
    fig = px.bar(df, x='item_name', y='sales', labels={'sales': 'Total Sales (MAD)','item_name':'Item'},
                 title='Overall Product Sales Pareto Chart') # Changed title slightly
    fig.add_trace(go.Scatter(x=df['item_name'], y=df['cumulativePercentage'], mode='lines+markers', name='Cumulative %', yaxis="y2")) # Added markers
    fig.update_layout(
        yaxis_title="Total Sales Value",
        yaxis2=dict(
            title='Cumulative Percentage',
            overlaying='y',
            side='right',
            range=[0, 105], # Extend range slightly
            showgrid=False,
        ),
         title_x=0.5 # Center title
    )
    # Define save path
    chart_filename = 'overall_pareto_chart.html' # Use a different name
    pie_path = os.path.join(settings.STATICFILES_DIRS[0], chart_filename)
    fig.write_html(pie_path)

    # Define chart link
    diagram_path = f"/static/{chart_filename}"
    print(f"Generated Overall Pareto chart: {diagram_path}") # Debugging
    return diagram_path #Return the chart path

def generate_sales_percentage_by_item_pie_chart(monthly_sales_data):
    """
    Generates a pie chart for sales percentages by item.
    
    Args:
        monthly_sales_data (list): A list of dictionaries, where each dict
                                   represents an order line like:
                                   {'item name': str, 'quantity': int, 'price selling': float}

    Returns:
        str: The static URL path to the generated chart HTML file, or None if no data.
    """
    if not monthly_sales_data:
        print("No sales data provided for the chart.")
        return None

    # Convert list of sales data dictionaries to DataFrame
    df = pd.DataFrame(monthly_sales_data)

    # Group by item name and sum the quantities
    sales_summary = df.groupby('item name')['quantity'].sum().reset_index()

    # Calculate total sales for percentage calculation
    total_sales = sales_summary['quantity'].sum()
    sales_summary['percentage'] = (sales_summary['quantity'] / total_sales) * 100

    # Create the pie chart using Plotly
    fig = px.pie(sales_summary, values='percentage', names='item name',
                 labels={'percentage': 'Sales Percentage', 'item name': 'Item'},
                 title='Sales Percentage by Item')

    # Update layout for better visualization
    fig.update_traces(textinfo='percent+label')  # Show percentage and label on the pie chart

    # Define save path (use a distinct name)
    chart_filename = 'sales_percentage_by_item_pie_chart.html'
    chart_save_path = os.path.join(settings.STATICFILES_DIRS[0], chart_filename)
    fig.write_html(chart_save_path)

    # Define static URL path
    chart_url_path = f"/static/{chart_filename}"
    print(f"Generated Sales Percentage by Item Pie Chart: {chart_url_path}")  # Debugging
    return chart_url_path



