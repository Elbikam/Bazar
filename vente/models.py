from django.db import models
from stock.models import*

# Create your models here.
class Client(models.Model):
    client_id = models.CharField(primary_key=True,max_length=30)

    def save(self, *args, **kwargs):
        if not self.client_id:
            # Generate the custom primary key value here
            # For example, you can use a counter to generate a unique number
            self.client_id = 'C-{:04d}'.format(self.pk)
        super().save(*args, **kwargs)

    def getInfo(self):
        pass
    def __str__(self):
        return self.client_id
class Revendeur(Client):
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    ville = models.CharField(max_length=30)
    matricule = models.CharField(max_length=30)
#////////////////////////////////////////////////////////////////////////////////////
class Sales(models.Model):
    Client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_created=True)

class Order(Sales):
    order_id = models.CharField(primary_key=True,max_length=30)
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate the custom primary key value here
            # For example, you can use a counter to generate a unique number
            self.order_id = 'S-{:04d}'.format(self.pk)
        super().save(*args, **kwargs)

class OrderDetails(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Barcode, on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    quantite = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)

    

    

    
    
    







    


