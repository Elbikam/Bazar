from typing import Any
from django.db import models
from stock.models import Item
import decimal
from django.urls import reverse
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime
from django.db.models import Q

#/////////////////// Abstract Class ////////////////////////////////////
class Commun(models.Model):
    date = models.DateTimeField(auto_now=True)

    @property
    def get_TVA(self):
        tva = self.get_HT*decimal.Decimal(0.2)
        return round(tva,2)
    @property
    def get_TTC(self):
        ttc = self.get_HT*decimal.Decimal(1.20)
        return round(ttc,2)

    class Meta: 
        abstract = True

#///////////////// Sale /////////////////////////////////
class Sale(Commun):
    @property
    def get_HT(self):
        bill_total = decimal.Decimal(0.00)
        orders = self.order_line_set.all()
        for order in orders:
            bill_total = bill_total + order.get_subtotal
        return bill_total
    
    @property
    def total_of_items(self):
        items = self.order_line_set.all()
        return items.count()
    def __str__(self):
         return f"SO{self.id}"


#////////////////// Devis //////////////////////////////// 
class Devis(Commun):
    customer = models.CharField(max_length=30)
    @property
    def get_HT(self):
        result = decimal.Decimal(0.00)
        orders = self.devis_line_set.all()
        for order in orders:
            result = result + order.get_subtotal
        return result
    @property
    def total_of_items(self):
        items = self.devis_line_set.all()
        return items.count()
#//////////////////// Vendor ///////////////////////////////
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    phone_whatsapp = models.CharField(
        max_length=13,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,13}$', message="Phone number must be entered in the format: '+212**********'. Up to 13 digits allowed.")]
    )
    @property
    def total_amount_received(self):
        total_received = decimal.Decimal(0.00)
        for sale in self.saletovendor_set.all():
            if hasattr(sale, 'cash'):
                total_received += sale.cash.amount_received
        return total_received
    
    @property
    def total_sales(self):
        total_sales = decimal.Decimal(0.00)
        for sale in self.saletovendor_set.all():
            total_sales += sale.get_TTC
        return total_sales

    @property
    def count_sales(self):
        return self.saletovendor_set.count()

    @property
    def balance(self):
        return self.total_amount_received - self.total_sales
    @property
    def report(self):
        l=[]
        for c in self.saletovendor_set.all():
            l.append(c.payment.amount_received)
        return l    
    def __str__(self):
        return f"{self.name}"

#/////////////////////  Sale  for specific customer ///////////////

class SaleToVendor(Sale):
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)


#////////////////////////////////// Inline order /////////////////////////////////
class Order_Line(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=30)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def get_subtotal(self):
        if self.price is None or self.quantity is None:
            return decimal.Decimal(0.00)
        return decimal.Decimal(self.quantity * self.price)

    def save(self, *args, **kwargs):
        if self.item:
           self.description = self.item.description
        super().save(*args, **kwargs)

    def __str__(self):
        return f"order: {self.pk} " 
#///////////////////////  Inline devis /////////////////////////////////
class Devis_Line(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=30)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    @property
    def get_subtotal(self):
        if self.price is None or self.quantity is None:
            return decimal.Decimal(0.00)
        return self.quantity * self.price
  
    def save(self, *args, **kwargs):
        if self.item:
           self.description = self.item.description
        super().save(*args, **kwargs)

    def __str__(self):
        return f"order_id: {self.pk} " 

#/////////////////////////// PAYMENT //////////////////////////////////////


class Payment(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_pay = models.BooleanField()
    def get_change(self):
        return self.amount_received - self.sale.get_TTC 


class Monthly_Payment(Payment):
    rest = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    @property
    def get_rest(self):
        return self.rest
    @get_rest.setter
    def get_rest(self,value):
        self.rest = value





