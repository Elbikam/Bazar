from typing import Any
from django.db import models
from stock.models import Item
import decimal
from django.urls import reverse
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
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
    is_returned = models.BooleanField(default=False) # change status flag whene return sales
    @property
    def get_HT(self):
        ht = decimal.Decimal(0.00)
        orders = self.order_line_set.all()
        for order in orders:
            ht = ht + order.get_subtotal
        return ht
    
    @property
    def total_of_items(self):
        items = self.order_line_set.all()
        return items.count()
    

    def __str__(self):
        return f"SO{self.id}"

#//////////////////////////// Return Sale ///////////////////////
class ReturnSale(Commun):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name="return_sale")
    so = models.CharField(max_length=30,default=None)
    @property
    def get_HT(self):
        ht = decimal.Decimal(0.00)
        orders = self.return_line_set.all()
        for order in orders:
            ht = ht + order.get_subtotal
        return ht
    
    @property
    def total_of_items(self):
        items = self.return_line_set.all()
        return items.count()
    def save(self, *args, **kwargs):
        # Ensure is_returned is updated when a return is created
        self.sale.is_returned = True
        self.sale.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Ensure is_returned is updated when the return is deleted
        self.sale.is_returned = False
        self.sale.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.pk}"
    
#/////////////////////////////// line Item /////////////////////
class LineItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=30)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    @property
    def get_subtotal(self):
        if self.price is None or self.quantity is None:
            return decimal.Decimal(0.00)
        return decimal.Decimal(self.quantity * self.price)
    @property
    def quantity_by_crtn(self):
        """Calculates how many cartons ."""
        if self.quantity > 0:
            c = self.quantity // self.item.qte_by_carton # Integer division
            u = self.quantity % self.item.qte_by_carton
        return f"carton:{c}|unit:{u}"
    def save(self, *args, **kwargs):
        if self.item:
            self.description = self.item.description
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


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
    balance  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
   
    @property
    def total_sales(self):
        total_sales = decimal.Decimal(0.00)
        for sale in self.saletovendor_set.all():
            total_sales += sale.get_TTC
        return total_sales

    @property
    def count_sales(self):
        return self.saletovendor_set.count()
    #Balance depend of monthly payment
    @property
    def get_balance(self):
        return self.balance
    @get_balance.setter
    def get_balance(self,value):
        self.balance = value
 
    def __str__(self):
        return f"{self.name}"

#/////////////////////  Sale  for specific customer ///////////////

class SaleToVendor(Sale):
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)

  
#////////////////////////////////// Inline order  and devis and return_sale/////////////////////////////////
class Order_Line(LineItem):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
 
class Devis_Line(LineItem):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE)
    
class Return_Line(LineItem):
    _sale = models.ForeignKey(ReturnSale, on_delete=models.CASCADE)    

#/////////////////////////// PAYMENT //////////////////////////////////////

class Payment(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_pay = models.BooleanField(default=False)

    @property
    def get_amount_received(self):
        return self.amount_received

    @get_amount_received.setter
    def get_amount_received(self,value):
        self.amount_received = value
    @property
    def get_ispay(self):
        return self.is_pay

    @get_ispay.setter
    def get_ispay(self,value):
        self.is_pay = value
    def get_change(self):
        return self.amount_received - self.sale.get_TTC 
    
    def current_month(self, current_month=timezone.now().month):
        """Default is current month"""
        queryset = SaleToVendor.objects.filter(date__month=current_month)
        return queryset

    def previous_month(self):
        """Returns the last month and the year."""
        now = timezone.now()
        last_month = now.month - 1 if now.month > 1 else 12
        last_month_year = now.year if now.month > 1 else now.year - 1
        return last_month, last_month_year

    


    

        


