# stock/management/commands/check_stock_alerts.py
from django.core.management.base import BaseCommand
from stock.models import StockAlert, Stock

class Command(BaseCommand):
    help = 'Check stock levels and send alerts'

    def handle(self, *args, **kwargs):
        alerts = []
        # Retrieve all stock items
        stock_items = Stock.objects.all()

        for stock_item in stock_items:
            # Get alerts associated with the current stock item
            alerts_for_item = StockAlert.objects.filter(stock=stock_item)
            for alert in alerts_for_item:
                if stock_item.total_quantity < alert.threshold:
                    alerts.append(f"{stock_item.id} is below the threshold of {alert.threshold}. Current stock: {stock_item.total_quantity}.")

        if alerts:
            self.stdout.write("\n".join(alerts))
        else:
            self.stdout.write("All items are above the alert threshold.")


