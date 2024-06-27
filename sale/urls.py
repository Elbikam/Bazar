from django.urls import path
from .views import (SaleOrderCreate,
                    SaleList
                    )

               

app_name="sale"

urlpatterns = [
    path('', SaleList.as_view(), name="sale-list"),
    path('add/',SaleOrderCreate.as_view(), name="sale-create"),
   
    ]