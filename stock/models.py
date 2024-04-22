from django.db import models
from django.urls import reverse
#############################
# Create your models here.

class Category(models.Model):
    CAT_CHOICES = [
    ('THE', 'THE'),
    ('PARFUM', 'PARFUM'),
    ('BOKHOUR', 'BOKHOUR'),
    ]

    name = models.CharField(max_length=10, choices=CAT_CHOICES)
    def __str__(self):
        """
        String representation of the category.
        """
        return f"Category: {self.name}"
    class Meta:
        verbose_name_plural = 'Categories'

class SubCategory(Category):
    SUBCAT_CHOICES = [
    ('CH', 'CHAARA'),
    ('MK', 'MKARKAB'),
    ('LAT', 'LATAFA'),
    ]
    sub_cat = models.CharField(max_length=10, choices=SUBCAT_CHOICES)
    def __str__(self):
        return f"sub_category: {self.sub_cat}"

class Item(models.Model):
    id = models.BigIntegerField(primary_key=True)
    date =models.DateField(auto_now_add=True)
    item  = models.CharField(max_length=10)
    description = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    
  
    def __str__(self):
        """
        String representation of the item.
        """
        return f"{self.item} - Category: {self.category}, Quantity: {self.quantity}"
    def get_absolute_url(self):
        return reverse("stock:item-detail", kwargs={"id": self.id})
   
    




    