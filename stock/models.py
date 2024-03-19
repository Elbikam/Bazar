from typing import Any
from django.db import models
##############################
import random
#############################
# Create your models here.
class Barcode(models.Model):
    code = models.CharField(primary_key=True,max_length=255, unique=True)
    date =models.DateField(auto_now=True)
    qte = models.PositiveBigIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    
    
    def __str__(self):
        return f"create at: {self.id}|{self.date}|{self.qte}"
    
class The(Barcode):
    type_the = [("C","Chaara"), ("M","Mkarkab"),]
    embalage_the =[("C","carton"),("Z","zanbile"),("Ca","cadeau"),("S","sac"), ("Kh","khshab"),]
    brand = models.CharField(max_length=50)
    type = models.CharField(max_length=20,choices=type_the)
    poid= models.IntegerField()
    ref = models.CharField(max_length=20)
    embalage= models.CharField(max_length=20,choices=embalage_the)

    def getBrand(self):
        return self.brand
    def getType(self):
        return self.type
    def getPoid(self):
        return self.poid
    def getEmbl(self):
        return self.embalage
    def getRef(self):
        return self.ref
    def __str__(self):
        return f"brand: {self.brand}|tyep:{self.type}|poid: {self.poid}"

    


    