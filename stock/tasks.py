# your_app/tasks.py

# your_app/tasks.py

from celery import shared_task
from stock.models import Stock

@shared_task
def reorder_stock(item_id, quantity):
    try:
        stock = Stock.objects.get(item_id=item_id)
        stock.current_quantity += quantity
        stock.save()
        print(f"Reordered {quantity} units of {stock.item.name}. New stock: {stock.current_quantity}")
        return f"Successfully reordered {quantity} units of {stock.item.name}"
    except Stock.DoesNotExist:
        print(f"Stock item with ID {item_id} not found.")
        return f"Failed to reorder: Stock item with ID {item_id} not found."