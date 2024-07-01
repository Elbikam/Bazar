from django.urls import path
from .views import (SaleOrderCreate,
                    SaleList,
                    SaleCreate,
                    )
      

app_name="sale"

urlpatterns = [
    path('',SaleList.as_view(), name="sale-list"),
    path('add/',SaleOrderCreate.as_view(), name="sale-create"),
    # path('sale/<int:pk>',SaleOrderUpdate.as_view(), name='sale-update'),
    
    ]