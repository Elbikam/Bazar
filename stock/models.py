from django.db import models
from django.urls import reverse
#############################
# Create your models here.

class Item(models.Model):
    id = models.BigIntegerField(primary_key=True)
    date =models.DateField(auto_now_add=True)
    item  = models.CharField(max_length=10)
    description = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.item} - Category: {self.description}, Quantity: {self.quantity}, price:{self.price}"
    # def get_absolute_url(self):
        # pass
    
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////   
class The(Item):
    SUBCAT_CHOICES = [
    ('CHAARA', 'CHAARA'),
    ('MKARKAB', 'MKARKAB'),
    ]
    PACKAGE_CHOICES = [
    ('CARTON', 'CARTON'),
    ('ZANBIL', 'ZANBIL'),
    ('CADEAU', 'CADEAU'),
     ('KHSHAB', 'KHSHAB'),
    ]
    WEIGHT_CHOICES = [
    ('200', '200'),
    ('500', '500'),
    ('1000', '1000'),
    ('2000', '2000'),
    ('3000', '3000'),
    ]
    REFERANCE_CHOICES = [
    ('9366', '9366'),
    ('9371', '9371'),
    ('9375', '9375'),
    ('4011', '4011'),
    ('41022', '41022'),
    ('3505B', '3505B'),
    ('41022', '41022'),
    ]

    category = models.CharField(max_length=15, choices=SUBCAT_CHOICES)
    packaging = models.CharField(max_length=15, choices=PACKAGE_CHOICES)
    weight = models.CharField(max_length=15, choices=WEIGHT_CHOICES)
    ref = models.CharField(max_length=15, choices=REFERANCE_CHOICES)
    def __str__(self):
        return f"The : {self.item} - Category: {self.category}, package: {self.packaging}, weight :{self.weight}, ref :{self.ref} "
    def get_absolute_url(self):
       return reverse("stock:the-detail", kwargs={"id":self.id})

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Parfum(Item):
    TYPE_CHOICES = [
    ('MAN', 'MAN'),
    ('WOMEN', 'WOMEN'),
    ('ALL', 'ALL'),
    ]
    VOLUM_CHOICES = [
    ('30 ml', '30 ml'),    
    ('50 ml', '50 ml'),
    ('100 ml', '100 ml'),
    ('500 ml', '500 ml'),
    ('1000 ml', '1000 ml'),
    ]
    sub_brand = models.CharField(max_length=20)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    volum = models.CharField(max_length=10, choices=VOLUM_CHOICES)
    def __str__(self):
        return f"Parfum : {self.item} - Category: {self.sub_brand}, type: {self.type}, volum: {self.volum} "
    def get_absolute_url(self):
       return reverse("stock:parfum-detail", kwargs={"id":self.id})





    