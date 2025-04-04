from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User

class Item(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    # category = models.CharField(max_length=10, choices=CAT_CHOICES)
    description = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)


    def __str__(self):
        return self.name
class The(Item):
    REF_CHOICES = [
        ('9366', '9366'),
        ('9371', '9371'),
        ('4011', '4011'),
        ('41022', '41022'),
        ('3505B', '3505B'),
    ]
    CAT_CHOICES = [
        ('CHENMEE', 'CHENMEE'),
        ('GUNPOWDER ', 'GUNPOWDER '),
    ]
    WEIGHT_CHOICES = [
        (100, '100g'),
        (200, '200g'),
        (500, '500g'),
        (1000, '1kg'),
        (2000, '2kg'),
        (3000, '3kg'),
    ]
  
    ref = models.CharField(max_length=15, choices=REF_CHOICES)
    category = models.CharField(max_length=15, choices=CAT_CHOICES)
    weight = models.IntegerField(choices=WEIGHT_CHOICES)


class Stock(models.Model):
    item = models.OneToOneField(Item, on_delete=models.DO_NOTHING, related_name='stock',primary_key=True)
    current_quantity = models.PositiveIntegerField(default=0)
    unit_by_carton = models.PositiveIntegerField(default=1)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    threshold_amount= models.PositiveIntegerField(default=0)
    reorder_point = models.PositiveIntegerField(default=0) #ADD This
    lead_time = models.IntegerField(default=7, help_text="Lead time in days")  # Add the lead_time field
    

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
    @property
    def total_value(self):
        """Calculates the total current value of the stock."""
        return self.current_quantity * self.cost_price
    def check_stock_alert(self):
        alerts = StockAlert.objects.filter(item=self)
        for alert in alerts:
            if self.current_quantity <= alert.threshold:
                # Logic to send alert, e.g., email, notification
                print(f"Alert! Stock for {self.item.name} is below threshold.")

    def __str__(self):
        return f"Stock for {self.item.name}: {self.current_quantity} units"


class Receipt(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now_add=True)  # Only set on creation
    bon_de_livraison = models.CharField(max_length=50)
    qte_total = models.PositiveIntegerField()
    qte_by_carton = models.PositiveIntegerField()

    @property
    def get_receipt_items(self):
        return self.items.count()
    @property
    def get_qte_carton(self):
        total_carton = 0
        items = self.items.all()
        for item in items:
            carton = item.quantity//item.unit_by_carton 
            total_carton += carton
        return total_carton    
    @property
    def get_qte_total(self):
        qteTotal = 0
        items = self.items.all()
        for item in items:
            qteTotal += item.quantity
        return qteTotal
        
    def __str__(self):
        return f"Receipt:{self.pk}"


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt,  related_name='items',on_delete=models.DO_NOTHING, null=True, verbose_name="Receipt",blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_by_carton = models.PositiveSmallIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field for cost price
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
        stock.cost_price = self.cost_price
        stock.save()
  
    @property
    def qte_by_carton(self):
        carton = self.quantity//self.unit_by_carton
        return carton

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
    item = models.ForeignKey(Stock, on_delete=models.DO_NOTHING,null=True, blank=True)
    threshold = models.PositiveIntegerField()  # Minimum stock level before alert
    created_at = models.DateTimeField(auto_now_add=True)
   
    def save(self, *args, **kwargs):
        # Check if an alert for the same item already exists
        if StockAlert.objects.filter(item=self.item).exists():
            # Update the threshold for the existing alert without calling save again
            StockAlert.objects.filter(item=self.item).update(threshold=self.threshold)
        else:
            # Create a new alert if no existing alert is found
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Alert for {self.item}: Threshold {self.threshold}"





