from typing import Any
from django.db import models
from stock.models import Item



# Create your models here.
#///////////////////////////// CUSTOMER ///////////////////////////////////
class Customer(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)

class Persone(Customer):
    
    def __str__(self):
        return self.name

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
    ID = 0
    
    sale_id = models.CharField(max_length=10, unique=True,primary_key=True)
    date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)

    def save(self,*args, **kwargs):
        self.sale_id = self.PREFEX + str(Sale.ID).zfill(6)
        Sale.ID += 1
        super(Sale,self).save(*args,**kwargs)
 

class Order(models.Model):
    so_id = models.ForeignKey(Sale, on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    description = models.CharField(max_length=30)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    
    def save(self, *args,**kwargs):
        self.description = self.item.description
        self.price = self.item.price
        self.amount = (self.quantity)*(self.item.price)
        super(Order,self).save(*args,**kwargs)


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