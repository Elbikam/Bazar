from django.urls import path
from .views import (SaleOrderCreate,
                    SaleList
                    )

               

app_name="sale"

urlpatterns = [
    path('',SaleOrderCreate.as_view(), name="sale-create"),
    path('list/', SaleList.as_view(), name="sale-list"),
    ]