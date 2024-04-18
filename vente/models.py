from typing import Any
from django.db import models
from stock.models import*
from django.forms import ModelForm


# Create your models here.
#//////////////////////////////////////////////////////////////////////////////////


class Customer(models.Model):
    PREFIX = 'C'
    Id = 1
    custom_id = models.CharField(max_length=5, editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.Id = Customer.Id
        Customer.Id += 1
        self.custom_id = self.PREFIX + str(Customer.Id).zfill(4)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.custom_id

class Revendeur(Customer):
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    ville = models.CharField(max_length=30)
    matricule = models.CharField(max_length=30)

    def getInfo(self):
        return self.nom
 
#////////////////////////////////////////////////////////////////////////////////////
class Sale(models.Model):
    PREFIX = 'S'
    Id = 1
    so = models.CharField(max_length=5, primary_key=True, editable=False)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    def save(self, *args, **kwargs):
        self.Id = Sale.Id
        Sale.Id += 1
        self.so = self.PREFIX + str(Sale.Id).zfill(4)
        super().save(*args, **kwargs)


class CreateOrder(models.Model):
    so_id = models.ForeignKey(Sale, on_delete=models.CASCADE)
    item = models.ForeignKey(Barcode, on_delete=models.CASCADE)
    description = models.CharField(max_length=30)
    qte = models.PositiveSmallIntegerField()
    price = models.FloatField(default=0.00, blank=False, null=False)



#///////////////////////////////////////////////////////////////////////////////
        

    

    
    
    







    


