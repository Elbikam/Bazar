from typing import Any
from django.db import models
from stock.models import*


# Create your models here.
#//////////////////////////////////////////////////////////////////////////////////
class Client(models.Model):
    pass

    def getInfo(self):
        pass

class Revendeur(Client):
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    ville = models.CharField(max_length=30)
    matricule = models.CharField(max_length=30)

    def getInfo(self):
        return self.nom

class Persone(Client):
    # you should invok superClass first 
    pass

 
#////////////////////////////////////////////////////////////////////////////////////
class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(auto_created=True)
class Order(Sale):
    pass

class OrderDetails(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Barcode, on_delete=models.CASCADE)
    qte = models.PositiveSmallIntegerField()

     
    def save(self,*args, **kwargs):
        
        self.description = self.item.brand
        self.price = self.item.price
    def __str__(self):
        return f"order Detail :{self.item}| {self.description}|{self.qte}|{self.price}"


#///////////////////////////////////////////////////////////////////////////////

    

    
    
    







    


