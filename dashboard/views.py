from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.forms import  LoginForm
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import requests
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from stock.models import Stock, StockAlert
from sale.models import Sale, Order_Line, Refund, Refund_Line, Dealer, SaleToDealer
from django.utils import timezone
from datetime import timedelta
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai


# ///////////////////////////////////////////////////////////////////////////////////////////////////////
class HomeView(TemplateView):
    template_name = 'dashboard/dashboard.html'  


def login_user(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard:dashboard')  # Include the app namespace
            else:
                return render(request, 'dashboard/login.html', {'form': form})
    return render(request, 'dashboard/login.html', {'form': form})



def logout_user(request):
    logout(request)  # Log the user out
    return redirect('dashboard:login')  # 


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

@csrf_exempt
def ask_gemini(request):
    if request.method != "POST":
        return render(request, 'dashboard/optimize_inventory.html', {"error": "Method not allowed"})

    query = request.POST.get('query', '')

    # Fetch stock data
    stocks = Stock.objects.all()
    ninety_days_ago = timezone.now() - timedelta(days=90)
    order_lines = Order_Line.objects.filter(sale__date__gte=ninety_days_ago).select_related('item', 'sale', 'item__item')
    refund_lines = Refund_Line.objects.filter(refund__date__gte=ninety_days_ago).select_related('item', 'refund')

    # Calculate monthly demand
    sales_dict = {}
    refunds_dict = {}
    for ol in order_lines:
        item_id = ol.item.item.id
        sales_dict[item_id] = sales_dict.get(item_id, 0) + ol.quantity
    for rl in refund_lines:
        item_id = rl.item.item.id
        refunds_dict[item_id] = refunds_dict.get(item_id, 0) + rl.quantity
    net_demand = {item_id: max(0, sales_dict.get(item_id, 0) - refunds_dict.get(item_id, 0)) for item_id in set(sales_dict) | set(refunds_dict)}
    days_in_period = (timezone.now() - ninety_days_ago).days or 1
    monthly_demand = {item_id: (qty / days_in_period) * 30 for item_id, qty in net_demand.items() if qty > 0}

    stock_summary = "\n".join([
        f"Item {stock.item.id} ({stock.item.name}): {stock.current_quantity} units, Cost: ${stock.item.cost_price}, Demand: {monthly_demand.get(stock.item.id, 0):.2f}/month, Lead Time: {stock.lead_time or 7} days"
        for stock in stocks
    ])

    # Calculate sales data
    sales_summary = {}
    profit_summary = {}
    for ol in order_lines:
        item_id = ol.item.item.id
        item_name = ol.item.item.name
        subtotal = float(ol.quantity * ol.price)
        profit = float(ol.quantity * (ol.price - ol.item.item.cost_price))
        
        if item_id not in sales_summary:
            sales_summary[item_id] = {"name": item_name, "total_ht": 0.0, "total_quantity": 0}
        if item_id not in profit_summary:
            profit_summary[item_id] = 0.0
        
        sales_summary[item_id]["total_ht"] += subtotal
        sales_summary[item_id]["total_quantity"] += ol.quantity
        profit_summary[item_id] += profit

    sales_data = "\n".join([
        f"Item {item_id} ({data['name']}): Total Sales (HT): ${data['total_ht']:.2f}, Total Sales (TTC): ${data['total_ht'] * 1.20:.2f}, Total Quantity Sold: {data['total_quantity']}, Total Profit: ${profit_summary[item_id]:.2f}"
        for item_id, data in sales_summary.items()
    ])

    # Updated MCP Prompt
    mcp_prompt = """**Model Context Protocol (MCP) for Inventory Management**

### Project Goal
Maximize profit, reduce costs, and optimize stock levels.

### Model Definitions
- **Stock**:
  - Fields: `current_quantity` (PositiveIntegerField), `unit_by_carton` (PositiveIntegerField), `lead_time` (IntegerField, default=7), `item` (OneToOneField to Item, primary key).
  - Properties: `total_value` = `current_quantity` * `item.cost_price`.
- **Item**:
  - Fields: `id` (BigIntegerField, primary key), `name` (CharField), `price` (DecimalField), `cost_price` (DecimalField).
- **Sale**:
  - Fields: `id` (AutoField, primary key), `date` (DateTimeField).
  - Properties: `get_HT` = Sum of `Order_Line.get_subtotal`, `get_TTC` = `get_HT` * 1.20.
- **Order_Line**:
  - Fields: `item` (ForeignKey to Stock), `quantity` (PositiveIntegerField), `price` (DecimalField).
  - Properties: `get_subtotal` = `quantity` * `price`.

### Business Rules
- **Demand Calculation**:
  - Monthly demand = ((Net sales - Net refunds) over the last 90 days / 90) * 30.
- **Stock Duration**:
  - Calculate stock duration in days as: `current_quantity / (monthly_demand / 30)`.
  - Subtract the lead time (in days) to determine safe stock duration.
  - Convert the final duration to weeks (assuming 7 days per week) for clarity.
- **Sales Metrics**:
  - Total sales value (HT) for an item = Sum of `Order_Line.get_subtotal` for that item over a period.
  - Total sales value (TTC) = Total HT * 1.20.
  - Profit per unit = `Order_Line.price` - `Item.cost_price`.
  - Total profit for an item = Sum of (`Order_Line.quantity` * (`Order_Line.price` - `Item.cost_price`)) over a period.
- **Inventory Turnover**:
  - Turnover rate = Total quantity sold over 90 days / Average inventory (where Average inventory = Current inventory for simplicity).
- **Holding Cost**:
  - Assume holding cost = 10% of `total_value` per month for simplicity (adjust based on actual data if available).

### AI Agent Responsibilities
- **Profit Maximization**:
  - Identify high-profit items (highest `total profit`) and recommend sales strategies (e.g., increase price, promote more).
  - Analyze pricing data (`Order_Line.price` vs. `Item.cost_price`) to suggest optimal selling prices (e.g., increase price if profit margin is low).
  - Predict future sales trends based on historical demand (e.g., extrapolate monthly demand).
  - Recommend strategies to reduce COGS (e.g., focus on high-margin items, reduce stock of low-profit items).
- **Cost Reduction**:
  - Analyze holding costs (`total_value * 0.10` per month) and recommend reducing excess inventory.
  - Suggest negotiating better terms with suppliers for items with high COGS (`Item.cost_price`).
  - Optimize stock levels to reduce waste (e.g., reduce overstock of slow-moving items).
- **Stock Optimization**:
  - Forecast demand using historical sales data (monthly demand).
  - Calculate reorder points: Reorder when safe stock duration < 2 weeks.
  - Identify stockouts (current_quantity = 0) and overstock (safe stock duration > 12 weeks).
  - Minimize holding costs by reducing excess inventory.
  - Recommend strategies for slow-moving items (safe stock duration > 12 weeks, e.g., discounts).
  - Use lead times to minimize safety stock (reorder earlier for items with longer lead times).
- **Reporting and Analysis**:
  - Generate KPIs: profit margin (total profit / total HT), inventory turnover, holding costs, stockout frequency.
  - Provide insights and recommendations based on data analysis.
  - Track effectiveness by comparing KPIs over time (requires historical data).

### Current Data
Item 1 (LWAD LWAAR): 64 units, Cost: $60.0, Demand: 12.0/month, Lead Time: 7 days, Total Value: $3840.00, Turnover Rate: 0.56, Monthly Holding Cost: $384.00
Item 2 (SMARA): 85 units, Cost: $70.0, Demand: 5.0/month, Lead Time: 7 days, Total Value: $5950.00, Turnover Rate: 0.18, Monthly Holding Cost: $595.00
Item 3 (SSS): 90 units, Cost: $65.0, Demand: 3.33/month, Lead Time: 7 days, Total Value: $5850.00, Turnover Rate: 0.11, Monthly Holding Cost: $585.00

### Sales Data
Item 1 (LWAD LWAAR): Total Sales (HT): $3600.00, Total Sales (TTC): $4320.00, Total Quantity Sold: 36, Total Profit: $1440.00
Item 2 (SMARA): Total Sales (HT): $1800.00, Total Sales (TTC): $2160.00, Total Quantity Sold: 15, Total Profit: $750.00
Item 3 (SSS): Total Sales (HT): $1100.00, Total Sales (TTC): $1320.00, Total Quantity Sold: 10, Total Profit: $450.00

### User Query
How can I maximize profit for my inventory?

Provide a concise response based on the data and query. Address the AI agent responsibilities relevant to the query, and include KPIs or recommendations to maximize profit, reduce costs, and optimize stock levels.
"""

    prompt = mcp_prompt.format(stock_data=stock_summary, sales_data=sales_data, user_query=query)

    try:
        response = gemini_model.generate_content(prompt)
        gemini_response = response.text
    except Exception as e:
        gemini_response = f"Error calling Gemini API: {str(e)}"

    context = {
        "total_items": stocks.count(),
        "total_value": sum(float(stock.total_value) for stock in stocks),
        "inventory_summary": "\n".join([
            f"{stock.item.name}: {stock.current_quantity} units, Demand: {monthly_demand.get(stock.item.id, 0):.2f}/month"
            for stock in stocks
        ]),
        "low_stock_summary": "Not computed in this view",
        "overstock_summary": "Not computed in this view",
        "optimization": "Not computed in this view",
        "diagrams": {},
        "stocks": list(stocks),
        "adjusted_demand": monthly_demand,
        "monthly_demand": monthly_demand,
        "sales_velocity": {},
        "gemini_response": gemini_response
    }
    return render(request, 'dashboard/optimize_inventory.html', context)

# Make Celery optional
try:
    from stock.tasks import reorder_stock
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

@csrf_exempt
def optimize_inventory(request):
    # Fetch stock data
    stocks = Stock.objects.all()
    total_items = stocks.count()
    total_value = sum(float(stock.total_value) for stock in stocks)

    # Debug: Print stock details
    print("Stock Values:", [(stock.item.name, stock.current_quantity, float(stock.item.cost_price), float(stock.total_value)) for stock in stocks])
    print("Total Value:", total_value)

    # Calculate net demand and sales trends (last 60days)
    ninety_days_ago = timezone.now() - timedelta(days=60)
    order_lines = Order_Line.objects.filter(sale__date__gte=ninety_days_ago).select_related('item', 'sale', 'item__item').prefetch_related('sale__sale_payments')
    refund_lines = Refund_Line.objects.filter(refund__date__gte=ninety_days_ago).select_related('item', 'refund')

    # Net demand: Sales - Refunds
    sales_dict = {}
    refunds_dict = {}
    sales_frequency = {}
    sales_by_period = {}
    profitability = {}
    dealer_sales = {}
    actual_revenue = {}
    unpaid_amounts = {}

    # Process sales with profit debugging
    for ol in order_lines:
        item_id = ol.item.item.id  # Use Item primary key since Stock's PK is item
        sales_dict[item_id] = sales_dict.get(item_id, 0) + ol.quantity
        sales_frequency[item_id] = sales_frequency.get(item_id, 0) + 1
        days_ago = (timezone.now() - ol.sale.date).days
        period = (90 - days_ago) // 30
        period = max(0, min(period, 2))
        if item_id not in sales_by_period:
            sales_by_period[item_id] = [0, 0, 0]
        sales_by_period[item_id][period] += ol.quantity
        cost_price = float(ol.item.item.cost_price)
        selling_price = float(ol.price)
        profit_per_unit = selling_price - cost_price
        profit = profit_per_unit * ol.quantity
        print(f"Order Line for {ol.item.item.name}: Quantity: {ol.quantity}, Selling Price: {selling_price}, Cost Price: {cost_price}, Profit/Unit: {profit_per_unit}, Total Profit: {profit}")
        profitability[item_id] = profitability.get(item_id, 0) + profit
        if hasattr(ol.sale, 'saletodealer'):
            dealer_id = ol.sale.saletodealer.dealer.id
            if item_id not in dealer_sales:
                dealer_sales[item_id] = {}
            dealer_sales[item_id][dealer_id] = dealer_sales[item_id].get(dealer_id, 0) + ol.quantity
        sale = ol.sale
        total_billed = float(sale.get_TTC)
        total_paid = sum(float(sp.amount_paid) for sp in sale.sale_payments.all()) if sale.sale_payments.exists() else 0
        actual_revenue[item_id] = actual_revenue.get(item_id, 0) + total_paid * (ol.quantity / sale.total_of_items)
        unpaid = total_billed - total_paid
        unpaid_amounts[item_id] = unpaid_amounts.get(item_id, 0) + unpaid * (ol.quantity / sale.total_of_items)

    # Process refunds
    for rl in refund_lines:
        item_id = rl.item.item.id  # Use Item primary key since Stock's PK is item
        refunds_dict[item_id] = refunds_dict.get(item_id, 0) + rl.quantity

    # Net demand with debugging
    net_demand = {item_id: max(0, sales_dict.get(item_id, 0) - refunds_dict.get(item_id, 0)) for item_id in set(sales_dict) | set(refunds_dict)}
    days_in_period = (timezone.now() - ninety_days_ago).days or 1
    monthly_demand = {item_id: (qty / days_in_period) * 30 for item_id, qty in net_demand.items() if qty > 0}
    print("Sales Dict:", sales_dict)
    print("Refunds Dict:", refunds_dict)
    print("Net Demand:", net_demand)
    print("Days in Period:", days_in_period)
    print("Monthly Demand:", monthly_demand)

    # Calculate sales velocity
    sales_velocity = {}
    for item_id, periods in sales_by_period.items():
        recent, mid, old = periods
        if mid + old > 0:
            velocity = (recent - (mid + old) / 2) / ((mid + old) / 2) * 100 if (mid + old) / 2 != 0 else 0
        else:
            velocity = 0 if recent == 0 else 100
        sales_velocity[item_id] = velocity

    # Calculate seasonal factors (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_sales = {stock.item.id: {i: 0 for i in range(12)} for stock in stocks}
    for ol in Order_Line.objects.filter(sale__date__gte=twelve_months_ago):
        item_id = ol.item.item.id
        month = (timezone.now().year * 12 + timezone.now().month - (ol.sale.date.year * 12 + ol.sale.date.month)) % 12
        monthly_sales[item_id][month] += ol.quantity

    seasonal_factors = {}
    for item_id, sales in monthly_sales.items():
        avg_sales = sum(sales.values()) / 12 if sum(sales.values()) > 0 else 1
        seasonal_factors[item_id] = [max(1, s / avg_sales if avg_sales > 0 else 1) for s in sales.values()]

    # Adjust demand for the current month
    current_month = timezone.now().month - 1
    adjusted_demand = {}
    for item_id, demand in monthly_demand.items():
        seasonal_factor = seasonal_factors.get(item_id, [1] * 12)[current_month]
        adjusted_demand[item_id] = demand * seasonal_factor

    # Dealer risk analysis
    dealers = Dealer.objects.all()
    dealer_risk = {dealer.id: float(dealer.total_unpaid) for dealer in dealers}
    dealer_summary = "\n".join([
        f"Dealer {dealer.name}: Total Unpaid ${dealer_risk.get(dealer.id, 0):.2f}"
        for dealer in dealers
    ])

    # Set default demand and metrics
    for stock in stocks:
        item_id = stock.item.id  # Use Item primary key
        if item_id not in monthly_demand:
            older_sales = Order_Line.objects.filter(sale__date__lt=ninety_days_ago, item=stock)
            older_refunds = Refund_Line.objects.filter(refund__date__lt=ninety_days_ago, item=stock)
            total_sales = sum(ol.quantity for ol in older_sales)
            total_refunds = sum(rl.quantity for rl in older_refunds)
            net_sales = total_sales - total_refunds
            if net_sales > 0:
                days = (ninety_days_ago - min(ol.sale.date for ol in older_sales)).days or 1
                monthly_demand[item_id] = (net_sales / days) * 30
            else:
                monthly_demand[item_id] = 15
            adjusted_demand[item_id] = monthly_demand[item_id] * seasonal_factors.get(item_id, [1] * 12)[current_month]
        if item_id not in sales_velocity:
            sales_velocity[item_id] = 0
        if item_id not in sales_frequency:
            sales_frequency[item_id] = 0
        if item_id not in profitability:
            profitability[item_id] = 0
        if item_id not in actual_revenue:
            actual_revenue[item_id] = 0
        if item_id not in unpaid_amounts:
            unpaid_amounts[item_id] = 0

    # Calculate reorder points
    lead_times = {stock.item.id: stock.lead_time or 7 for stock in stocks}
    reorder_points = {}
    for item_id, demand in adjusted_demand.items():
        reorder_points[item_id] = (demand / 30) * lead_times.get(item_id, 7) + (demand / 2)

    # Prepare inventory summary
    inventory_summary = "\n".join([
        f"{stock.item.name}: {stock.current_quantity} units, "
        f"Price: ${stock.item.price}, Cost: ${stock.item.cost_price}, "
        f"Base Demand: {monthly_demand.get(stock.item.id, 0):.2f}/month, "
        f"Adjusted Demand: {adjusted_demand.get(stock.item.id, monthly_demand.get(stock.item.id, 0)):.2f}/month, "
        f"Sales Velocity: {sales_velocity.get(stock.item.id, 0):.1f}%, "
        f"Sales Frequency: {sales_frequency.get(stock.item.id, 0)} transactions, "
        f"Total Profit: ${profitability.get(stock.item.id, 0):.2f}, "
        f"Actual Revenue: ${actual_revenue.get(stock.item.id, 0):.2f}, "
        f"Unpaid Amount: ${unpaid_amounts.get(stock.item.id, 0):.2f}, "
        f"Reorder Point: {reorder_points.get(stock.item.id, 0):.0f} units"
        for stock in stocks
    ])

    # Identify low stock and overstock with debugging
    low_stock = []
    overstock = []
    holding_cost_per_unit = 0.50
    for stock in stocks:
        item_id = stock.item.id
        demand = adjusted_demand.get(item_id, monthly_demand.get(item_id, 0))
        threshold = StockAlert.objects.filter(item=stock).first().threshold if StockAlert.objects.filter(item=stock).exists() else demand / 2
        overstock_threshold = demand * 3
        print(f"Stock: {stock.item.name}, Current: {stock.current_quantity}, Demand: {demand}, Threshold: {threshold}, Overstock Threshold: {overstock_threshold}")
        if stock.current_quantity < threshold:
            low_stock.append(stock)
        elif stock.current_quantity > overstock_threshold:
            overstock.append(stock)
    low_stock_summary = "\n".join([f"{s.item.name}: {s.current_quantity} units" for s in low_stock])
    overstock_summary = "\n".join([f"{s.item.name}: {s.current_quantity} units" for s in overstock])

    # Dealer sales breakdown
    dealer_sales_summary = "\n".join([
        f"Item {stock.item.name}:\n" + "\n".join([
            f"  Dealer {Dealer.objects.get(id=dealer_id).name}: {qty} units"
            for dealer_id, qty in dealer_sales.get(stock.item.id, {}).items()
        ])
        for stock in stocks if stock.item.id in dealer_sales
    ])

    # MCP Prompt
    mcp_prompt = """
**Model Context Protocol (MCP) for Inventory Optimization**

### Model Definitions
- **Stock**:
  - Fields: `current_quantity` (PositiveIntegerField), `unit_by_carton` (PositiveIntegerField), `lead_time` (IntegerField, default=7), `item` (OneToOneField to Item, primary key).
  - Properties: `total_value` = `current_quantity` * `item.cost_price`, `quantity_by_crtn` = (cartons, units).
- **Item**:
  - Fields: `id` (BigIntegerField, primary key), `name` (CharField), `description` (CharField), `price` (DecimalField), `cost_price` (DecimalField).
- **Sale**:
  - Inherits from Commun: `user` (ForeignKey to User), `date` (DateTimeField).
  - Properties: `get_HT` = Sum of `Order_Line.get_subtotal`, `get_TTC` = `get_HT` * 1.20, `total_of_items` = count of `Order_Line`.
- **Order_Line**:
  - Inherits from LineItem: `item` (ForeignKey to Stock), `quantity` (PositiveIntegerField), `price` (DecimalField).
  - Properties: `get_subtotal` = `quantity` * `price`.
- **Refund**:
  - Inherits from Commun: `sale` (OneToOneField to Sale), `reason` (CharField).
  - Properties: `get_HT` = Sum of `Refund_Line.get_subtotal`.
- **Refund_Line**:
  - Inherits from LineItem: Links to `Refund`.

### Relationships
- `Stock` links to `Item` (one-to-one, primary key).
- `Order_Line` links to `Sale` and `Stock` (many-to-one).
- `Refund_Line` links to `Refund` and `Stock` (many-to-one).

### Business Rules
- **Demand Calculation**:
  - Monthly demand = ((Net sales - Net refunds) over the last 90 days / 90) * 30.
  - Net demand = Total `Order_Line.quantity` - Total `Refund_Line.quantity`.
- **Seasonal Trends**:
  - Adjust monthly demand with seasonal factors.
- **Sales Velocity**:
  - Percentage change in sales between periods.
- **Low Stock**:
  - `current_quantity` < `threshold` (default: demand / 2).
- **Overstock**:
  - `current_quantity` > 3 * demand.
- **Profitability**:
  - Profit per unit = `Order_Line.price` - `Item.cost_price`.
- **Reorder Point**:
  - (Adjusted Demand / 30) * `lead_time` + (demand / 2).
"""

    # Google Gemini API optimization
    prompt = f"""
{mcp_prompt}

Analyze the following inventory and sales data:
- Total items: {total_items}
- Total value (at cost): ${total_value:.2f}
- Inventory:
{inventory_summary}
- Low stock items (below threshold):
{low_stock_summary}
- Overstocked items (over 3 months' demand):
{overstock_summary}
- Holding cost per unit per month: ${holding_cost_per_unit}
- Dealer Risk Analysis:
{dealer_summary}
- Dealer Sales Breakdown:
{dealer_sales_summary}
- Adjusted Demand per Item (Seasonal):
{inventory_summary}
- Actual Revenue and Unpaid Amounts per Item:
{'\n'.join([f'  {stock.item.name}: Revenue ${actual_revenue.get(stock.item.id, 0):.2f}, Unpaid ${unpaid_amounts.get(stock.item.id, 0):.2f}' for stock in stocks])}

Provide:
1. Summary of current inventory state.
2. Recommendations to maximize benefits.
3. Recommendations to reduce costs.
4. Optimal stock levels for each item.
"""
    try:
        api_key = settings.GEMINI_API_KEY
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7}
        }
        response = requests.post(f"{url}?key={api_key}", json=data, headers=headers)
        response.raise_for_status()
        optimization = response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        reorder_quantities = "\n".join([
            f"Reorder {max(0, int(demand * 2 - stock.current_quantity))} units of {stock.item.name} "
            f"({max(0, (int(demand * 2 - stock.current_quantity) // stock.unit_by_carton))} cartons)"
            for stock, demand in [(s, adjusted_demand.get(s.item.id, monthly_demand.get(s.item.id, 15))) for s in low_stock]
        ])
        optimal_levels = "\n".join([
            f"{stock.item.name}: {int(adjusted_demand.get(stock.item.id, monthly_demand.get(stock.item.id, 15)) * (2 if sales_velocity.get(stock.item.id, 0) > 20 else 1.5))} units"
            for stock in stocks
        ])
        holding_cost_savings = sum((stock.current_quantity - adjusted_demand.get(stock.item.id, monthly_demand.get(stock.item.id, 15)) * 3) * holding_cost_per_unit
                                   for stock in overstock if stock.current_quantity > adjusted_demand.get(stock.item.id, monthly_demand.get(stock.item.id, 15)) * 3)
        pricing_adjustments = "\n".join([
            f"{'Increase' if sales_velocity.get(stock.item.id, 0) > 20 else 'Decrease'} price for {stock.item.name} "
            f"by {5 if sales_velocity.get(stock.item.id, 0) > 20 else 3}% "
            f"(velocity: {sales_velocity.get(stock.item.id, 0):.1f}%)"
            for stock in stocks
        ])
        dealer_priorities = "\n".join([
            f"Prioritize stock for Dealer {Dealer.objects.get(id=dealer_id).name} (Unpaid: ${unpaid:.2f})"
            for dealer_id, unpaid in sorted(dealer_risk.items(), key=lambda x: x[1], reverse=True)[:2]
        ])
        optimization = f"Error: {str(e)}\nFalling back to default recommendations:\n" \
                       f"Summary: {total_items} items worth ${total_value:.2f}. Consider reordering low stock items.\n" \
                       f"Maximize Benefits: {pricing_adjustments}\n" \
                       f"Reduce Costs: {reorder_quantities if low_stock else 'No immediate reordering needed.'}\n" \
                       f"Potential Holding Cost Savings: ${holding_cost_savings:.2f}/month by reducing overstock.\n" \
                       f"Dealer Priorities: {dealer_priorities}\n" \
                       f"Optimal Levels:\n{optimal_levels}"

    # Trigger reordering for low stock
    for stock in low_stock:
        item_id = stock.item.id
        demand = adjusted_demand.get(item_id, monthly_demand.get(item_id, 15))
        reorder_quantity = max(0, int(demand * 2 - stock.current_quantity))
        if reorder_quantity > 0:
            if CELERY_AVAILABLE:
                try:
                    if not item_id or reorder_quantity <= 0:
                        optimization += f"\nFailed to reorder {stock.item.name}: Invalid item ID or quantity."
                        continue
                    task = reorder_stock.delay(item_id, reorder_quantity)
                    optimization += f"\nTriggered reorder: {reorder_quantity} units of {stock.item.name} (Task ID: {task.id})"
                except Exception as e:
                    optimization += f"\nFailed to trigger reorder for {stock.item.name}: {str(e)}"
            else:
                try:
                    stock.get_current_qte += reorder_quantity
                    stock.save()
                    optimization += f"\nSynchronously reordered: {reorder_quantity} units of {stock.item.name}. New stock: {stock.current_quantity}"
                except Exception as e:
                    optimization += f"\nFailed to synchronously reorder {stock.item.name}: {str(e)}"

    # Generate diagrams
    product_names = [stock.item.name for stock in stocks]
    stock_levels = [stock.current_quantity for stock in stocks]
    demand_levels = [adjusted_demand.get(stock.item.id, monthly_demand.get(stock.item.id, 0)) for stock in stocks]
    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    x = range(len(product_names))
    plt.bar(x, stock_levels, bar_width, label='Stock', color='skyblue')
    plt.bar([i + bar_width for i in x], demand_levels, bar_width, label='Adjusted Demand', color='salmon')
    plt.xlabel('Products')
    plt.ylabel('Quantity')
    plt.title('Stock vs. Adjusted Monthly Demand')
    plt.xticks([i + bar_width / 2 for i in x], product_names, rotation=45, ha='right')
    plt.legend()
    bar_path = os.path.join(settings.STATICFILES_DIRS[0], 'stock_demand_bar.png')
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()

    df = pd.DataFrame({
        'product_name': product_names,
        'value': [float(stock.total_value) for stock in stocks]
    })
    fig = px.pie(df, names='product_name', values='value', title='Inventory Value Distribution (Cost)')
    pie_path = os.path.join(settings.STATICFILES_DIRS[0], 'cost_pie.html')
    fig.write_html(pie_path)

    return render(request, 'dashboard/optimize_inventory.html', {
        "total_items": total_items,
        "total_value": total_value,
        "inventory_summary": inventory_summary,
        "low_stock_summary": low_stock_summary,
        "overstock_summary": overstock_summary,
        "optimization": optimization,
        "diagrams": {
            "stock_demand_bar": "/static/stock_demand_bar.png",
            "cost_pie": "/static/cost_pie.html"
        },
        "stocks": list(stocks),
        "adjusted_demand": adjusted_demand,
        "monthly_demand": monthly_demand,
        "sales_velocity": sales_velocity
    })