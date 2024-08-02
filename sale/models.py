from typing import Any
from django.db import models
from stock.models import Item
import decimal
from django.urls import reverse
# Create your models here.
#///////////////////////////// CUSTOMER ///////////////////////////////////
class Customer(models.Model):
    name = models.CharField(max_length=30)
    class Meta:
        abstract = True

class Persone(Customer):
    pass

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
    PREFEX = 'SO'
    sale_id = models.CharField(max_length=10)
    customer = models.CharField(max_length=10,null=True)
    date = models.DateTimeField(auto_now=True)
     

    def save(self, *args, **kwargs):
        if not self.sale_id:
            super().save(*args, **kwargs)  
            self.sale_id = f"{self.PREFEX}{self.pk}"
            self.save(update_fields=['sale_id'])
        else:
            super(Sale, self).save(*args, **kwargs)


    def get_absolute_url(self):
       return reverse("sale:sale-detail", kwargs={"id":self.pk})
       
        
        
    def __str__(self):
        return f"sale id: {self.sale_id}"
    @property
    def get_HT(self):
        bill_total = decimal.Decimal(0.00)
        orders = self.order_set.all()
        for order in orders:
            bill_total = bill_total + order.get_subtotal_with_discount
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
    item = models.CharField(max_length=13)
    description = models.CharField(max_length=30)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Fixed amount discount
    
    @property
    def get_subtotal(self):
        # Ensure price and quantity are not None
        if self.price is None or self.quantity is None:
            return decimal.Decimal(0.00)
        return self.quantity * self.price

    @property
    def get_subtotal_with_discount(self):
        subtotal = self.get_subtotal
        discount_total = self.discount * self.quantity
        subtotal_with_discount = subtotal - discount_total
        return max(subtotal_with_discount, decimal.Decimal(0))

    def save(self, *args, **kwargs):
        self.item_id = Item.objects.get(id=self.item_id_id)
        self.description = self.item_id.description
        self.price = self.item_id.price
        super().save(*args, **kwargs)

    

#/////////////////////////// PAYMENT //////////////////////////////////////

class Payment(models.Model):
    sale_id = models.ForeignKey(Sale, on_delete=models.CASCADE)
   
class Cash(Payment):
    total = models.DecimalField(max_digits=6, decimal_places=2)
    amount_received = models.FloatField(default=False, blank=False, null=False)
    balance = models.FloatField(default=False, blank=False, null=False)

    def save(self,*args,**kwargs):
        amt_received = self.amount_received
        self.balance = amt_received - self.total
        super(Cash,self).save(*args,**kwargs)
     

class Cheque(Payment):
    pass


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=10, unique=True)
    customer_name = models.CharField(max_length=100)
    issue_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.customer_name}"
