from django.core.management.base import BaseCommand
from stock.models import Stock, StockAlert, Notification
from django.db.models import F  # Import F

class Command(BaseCommand):
    help = 'Check stock levels and notify if below threshold'

    def handle(self, *args, **options):
        # Get all stock alerts where the stock is below the threshold
        low_stock_items = StockAlert.objects.filter(
            item__current_quantity__lt=F('threshold')
        ).select_related('item')

        if low_stock_items.exists():
            for alert in low_stock_items:
                # Create a notification for the low stock alert
                Notification.objects.create(
                    title='Low Stock Alert',
                    message=f'Stock level for {alert.item} is low. Current quantity: {alert.item.current_quantity}.',
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Notification sent for {alert.item} with quantity {alert.item.current_quantity}.'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('All items are above threshold. No notifications sent.'))





