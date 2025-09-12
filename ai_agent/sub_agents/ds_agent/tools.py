import datetime
from django.db.models import Max
from stock.models import ReceiptItem,Stock
date_today = datetime.date.today()
import decimal


def calculate_lead_time(item_id:int,current_date=date_today)->dict:
    """Calculates the lead time for the stock item in days.
    Args:
        item_id: item_id.
        default_date: current_date.
    Returns:
        A dictionary with the lead time , e.g., {'status': 'success', 'result':53}

    """
    last_reorder= ReceiptItem.objects.filter(item_id=item_id).aggregate(Max('receipt__date'))['receipt__date__max']
    if last_reorder:
        lead_time = current_date - last_reorder
        return {"status": "success", "lead_time": lead_time.days}
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

