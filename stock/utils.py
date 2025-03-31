#In utils.py
from django.db.models import F, Sum
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from sale.models import *
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

def get_sales_data(stock):
    """Calculates the net sales (sales - refunds) for a given stock item over the last 90 days."""
    today = timezone.now().date()
    ninety_days_ago = today - timedelta(days=90)

    sales_total = Order_Line.objects.filter(
        item=stock,
        sale__date__range=[ninety_days_ago, today]
    ).aggregate(total_sales=Sum('price * quantity'))['total_sales'] or Decimal(0)

    refunds_total = Refund_Line.objects.filter(
        item=stock,
        refund__date__range=[ninety_days_ago, today]
    ).aggregate(total_refunds=Sum('price * quantity'))['total_refunds'] or Decimal(0)

    net_sales = sales_total - refunds_total
    return net_sales

def generate_stock_sales_report():
    today = timezone.now().date()
    ninety_days_ago = today - timedelta(days=90)
    report_data = []

    # Retrieve the specific Stock objects you are interested in.
    # IMPORTANT: Adjust the filtering criteria below to match your actual data!
    # Assuming the 'name' field exists on your Item model
    items_to_report = [
        ("code_lwaad", "LWAD LWAAR"),  # (Stock Filter, Item Name)
        #("SMARA", "SMARA"), # (Stock Filter, Item Name)
        #("SSS", "SSS"),   # (Stock Filter, Item Name)
    ]

    for stock_filter, item_name in items_to_report:
        try:
            # First, try to find the Stock by the item's name. This assumes your item.name is unique
            stock = Stock.objects.get(item__name=item_name)

        except Stock.DoesNotExist:
            print(f"Stock not found for item name: {item_name}")
            continue # Skip to the next item

        item = stock.item
        current_quantity = stock.current_quantity
        cost_price = item.cost_price
        selling_price = item.price
        total_value = current_quantity * cost_price
        potential_revenue = current_quantity * selling_price

        # Calculate Net Sales (Sales - Refunds) over the last 90 days
        sales_total = Order_Line.objects.filter(
            item=stock,  # Filter by the Stock object
            sale__date__range=[ninety_days_ago, today]  # Access the date from the sale
        ).aggregate(total_sales=Sum(F('price') * F('quantity')))['total_sales'] or Decimal(0) # Correctly use F expressions

        refunds_total = Refund_Line.objects.filter(
            item=stock,  # Filter by the Stock object
            refund__date__range=[ninety_days_ago, today]  # Access the date from the refund
        ).aggregate(total_refunds=Sum(F('price') * F('quantity')))['total_refunds'] or Decimal(0) # Correctly use F expressions

        net_sales = sales_total - refunds_total

        # Calculate Monthly Demand
        monthly_demand = (net_sales / 90) * 30 if net_sales > 0 else Decimal(0)

        # Calculate Stock Duration (Weeks)
        if monthly_demand > 0:
            stock_duration_days = (current_quantity / (monthly_demand / 30)) - stock.lead_time
            stock_duration_weeks = stock_duration_days / 7
        else:
            stock_duration_weeks = float('inf') # Or a large number if no demand

        report_data.append({
            'Item Name': item.name,
            'Current Quantity': current_quantity,
            'Cost Price': cost_price,
            'Selling Price': selling_price,
            'Total Value': total_value,
            'Potential Revenue': potential_revenue,
            'Net Sales (90 days)': net_sales,
            'Monthly Demand': monthly_demand,
            'Stock Duration (Weeks)': stock_duration_weeks
        })

    return report_data