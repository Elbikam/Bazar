from django.db import models
#############################
# Create your models here.
CAT_CHOICES = [
    ('THE', 'THE'),
    ('PARFUM', 'PARFUM'),
    ('BOKHOUR', 'BOKHOUR'),
    ]

SUBCAT_CHOICES = [
    ('CH', 'CHAARA'),
    ('MK', 'MKARKAB'),
    ('LAT', 'LATAFA'),
    ]

class Category(models.Model):
    name = models.CharField(max_length=10, choices=CAT_CHOICES)
class SubCategory(Category):
    sub_cat = models.CharField(max_length=10, choices=SUBCAT_CHOICES)

class Item(models.Model):
    id = models.BigIntegerField(primary_key=True, primary_key=True)
    date =models.DateField(auto_now_add=True)
    item  = models.CharField(max_length=10)
    description = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    qte_entry = models.PositiveIntegerField()
    price = models.FloatField(max_digits=5,decimal_places=2)
    qte_onHand = models.PositiveIntegerField()
  
    def __str__(self):
        """
        String representation of the item.
        """
        return f"{self.item} - Category: {self.category}, Quantity: {self.qte_entry}"
   
    




    