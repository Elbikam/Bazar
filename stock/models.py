from typing import Any
from django.db import models
from datetime import date


#############################
# Create your models here.
class Barcode(models.Model):
    id = models.BigIntegerField(primary_key=True)
    date =models.DateField(auto_now_add=True)
    brand = models.CharField(max_length=20)
    qte_entry = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    qte_onHand = models.PositiveIntegerField()
   


      
    def __str__(self):
        return f"create at: {self.code}|{self.date}|{self.qte}"
    
class The(Barcode):
    type_the = [("chaara","Chaara"), ("mkarkab","Mkarkab"),]
    embalage_the =[("carton","carton"),("zanbil","zanbile"),("cadeau","cadeau"),("sac","sac"), ("Khshab","khshab"),]
    type = models.CharField(max_length=20,choices=type_the)
    poid= models.CharField(max_length=20)
    ref = models.CharField(max_length=20)
    embalage= models.CharField(max_length=20,choices=embalage_the)
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
            print("Okey")
        except:
            print("alrady exit ")
                

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
        return f"{self.brand}|tyep:{self.type}|poid: {self.poid}|qte: {self.qte}"

#//////////////////////////////////////////////////////////////////////////////////////////
class Parfum(Barcode):
    type_p = [('M','Man'),('W','Woman'),('A','All')]
    sub_brand = models.CharField(max_length=30)
    type_parfum = models.CharField(max_length=30 ,choices=type_p)
    volume = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
            print("Okey")
        except:
            print("alrady exit ")
    def __str__(self):
        return f"{self.brand} | {self.sub_brand} | {self.type_parfum}"        
                




    