from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

class Item(models.Model):
    CAT_CHOICES = [
        ('THE VERT', 'THE VERT'),
        ('BAZAR', 'BAZAR'),
        ('PARFUM', 'PARFUM')
    ]

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    category = models.CharField(max_length=10, choices=CAT_CHOICES)
    description = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return self.name


class Stock(models.Model):
    item = models.OneToOneField(Item, on_delete=models.DO_NOTHING, related_name='stock')
    current_quantity = models.PositiveIntegerField(default=0)
    unit_by_carton = models.PositiveIntegerField(default=1)

    @property
    def get_current_qte(self):
        return self.current_quantity
    
    @get_current_qte.setter
    def get_current_qte(self,value):
        self.current_quantity = value
    
    @property
    def qte_by_carton(self):
        return self.unit_by_carton
    @qte_by_carton.setter
    def qte_by_carton(self,value):
        self.unit_by_carton = value

    @property
    def quantity_by_crtn(self):
        """Calculates how many cartons."""
        if self.current_quantity > 0:
            cartons = self.current_quantity // self.unit_by_carton
            units = self.current_quantity % self.unit_by_carton
            return f"{cartons} cartons | {units} Unit"
        return "0 cartons | 0 units"
    
    def check_stock_alert(self):
        alerts = StockAlert.objects.filter(item=self)
        for alert in alerts:
            if self.current_quantity <= alert.threshold:
                # Logic to send alert, e.g., email, notification
                print(f"Alert! Stock for {self.item.name} is below threshold.")

    def __str__(self):
        return f"Stock for {self.item.name}: {self.current_quantity} units"


class Receipt(models.Model):
    date = models.DateField(auto_now_add=True)  # Only set on creation
    bon_de_livrason = models.CharField(max_length=50)
    qte_total = models.PositiveIntegerField()
    qte_by_carton = models.PositiveIntegerField()

    def receipt_items(self):
        return self.items.all()

    def __str__(self):
        return f"Receipt:{self.pk}"


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, related_name='items', on_delete=models.DO_NOTHING, null=True, verbose_name="Receipt")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_by_carton = models.CharField(max_length=50, blank=True, null=True)
    def save(self, *args, **kwargs):
        """
        Overrides the save method to ensure the Stock entry for the item exists.
        If it does not exist, create it. Then, update the Stock quantity.
        """
        # Check if the Stock for the item exists; if not, create it
        stock, created = Stock.objects.get_or_create(item=self.item)
        
        # Save the ReceiptItem
        super().save(*args, **kwargs)
        stock.get_current_qte += self.quantity
        stock.qte_by_carton = self.unit_by_carton
        stock.save()
  


    def delete(self, *args, **kwargs):
        """
        Overrides the delete method to update the related Stock
        quantity when a ReceiptItem is deleted.
        """
        super().delete(*args, **kwargs)
        # Update the stock after deleting the ReceiptItem
        self.item.stock.update_total_quantity()

    def __str__(self):
        return f"{self.item.name}: {self.quantity} units"



class StockAlert(models.Model):
    item = models.OneToOneField(Stock, on_delete=models.DO_NOTHING,null=True, blank=True)
    threshold = models.PositiveIntegerField()  # Minimum stock level before alert
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.item}: Threshold {self.threshold}"





class Notification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.title