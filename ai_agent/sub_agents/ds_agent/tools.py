import datetime
from django.db.models import Max
from stock.models import ReceiptItem,Stock
date_today = datetime.date.today()
import decimal
from math import sqrt


def calculate_lead_time(item_id:int)->dict:
    """Calculates the lead time for the stock item in days.
    Args:
        item_id: item_id.
        default_date: current_date.
    Returns:
        A dictionary with the lead time , e.g., {'status': 'success', 'result':53}

    """
    current_date=date_today
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
    result = round(total_monthly_waherhousing_costs*12/number_of_pallet_space,2)
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
    return sqrt((2*d*s)/h)