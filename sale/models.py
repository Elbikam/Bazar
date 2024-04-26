from django.db import models
#from django_autoslug.fields import AutoSlugField

# Create your models here.









class Sale(models.Model):
    PAYMENT_CHOICES = [
    ('CS', 'CASH'),
   
]
    pass

class Order(Sale):
    pass



class Devis(Sale):
    pass