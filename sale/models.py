from typing import Any
from django.db import models
from stock.models import Item
import decimal
from django.urls import reverse

# Create your models here.
#///////////////////////////// CUSTOMER ///////////////////////////////////
class Customer(models.Model):
    customer = models.CharField(max_length=30)
    def __str__(self):
        return f"customer id{self.pk}"



class Persone(Customer):
    pass
    def __str__(self):
        return f"{self.customer}" 

class Revendeur(Customer):
    PREFX = 'R'
    ID = 1
    account  = models.CharField(max_length=13, primary_key=True)
    city = models.CharField(max_length=20)
    matricule = models.CharField(max_length=20)

    def save(self,*args, **kwargs):
        self.account = self.PREFX + str(Revendeur.ID).zfill(6)
        Revendeur.ID += 1
        super(Revendeur,self).save(*args,**kwargs)
    def __str__(self):
        return f"account: {self.account}|first name:{self.first_name}|last name: {self.last_name}| city: {self.city}| matricul : {self.matricule}"
#/////////////////////////////// Sale ////////////////////////////////////////////
class Sale(models.Model):
    # Fields specific to the sale
    sale_id = models.CharField(max_length=10)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.sale_id:
            super().save(*args, **kwargs)
            self.sale_id = f"SO{self.pk}"
            self.save(update_fields=['sale_id'])
        else:
            super(Sale, self).save(*args, **kwargs)
    

    def get_absolute_url(self):
        return reverse("sale:sale-detail", kwargs={"pk":self.pk})
    
    def __str__(self):
        return f"sale id: {self.sale_id}"
    @property
    def get_HT(self):
        bill_total = decimal.Decimal(0.00)
        orders = self.order_set.all()
        for order in orders:
            bill_total = bill_total + order.get_subtotal
        return bill_total
    @property
    def get_TVA(self):
        tva = self.get_HT*decimal.Decimal(0.2)
        return round(tva,2)
    @property
    def get_TTC(self):
        ttc = self.get_HT*decimal.Decimal(1.20)
        return round(ttc,2)
    @property
    def total_of_items(self):
        items = self.order_set.all()
        return len(items)
        

class Order(models.Model):
    so_id = models.ForeignKey(Sale, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=30)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    @property
    def get_subtotal(self):
        if self.price is None or self.quantity is None:
            return decimal.Decimal(0.00)
        return self.quantity * self.price

    
    def save(self, *args, **kwargs):
        if self.item_id:
           self.description = self.item_id.description
           self.price = self.item_id.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"order: {self.pk} "

#/////////////////////////// PAYMENT //////////////////////////////////////

class Payment(models.Model):
    sale_id = models.OneToOneField(Sale, on_delete=models.CASCADE)
    class Meta:
        abstract = True 

class Cash(Payment):
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_pay = models.BooleanField()

    def get_change(self):
        change = self.amount_received - self.sale_id.get_TTC 
        return change

   
     

class Cheque(Payment):
    pass


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=10, unique=True)
    customer_name = models.CharField(max_length=100)
    issue_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.customer_name}"
