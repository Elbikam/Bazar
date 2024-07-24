from django.urls import path
from .views import (SaleOrderCreate,
                    SaleList,
                    SaleCreate,
                    SaleDetailView
                    )
      

app_name="sale"

urlpatterns = [
    path('',SaleList.as_view(), name="sale-list"),
    path('add/', SaleOrderCreate.as_view(), name='sale_create'),
    path('detail/<int:id>', SaleDetailView.as_view(), name="sale-detail"),
   
   
    
    ]