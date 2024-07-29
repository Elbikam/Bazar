from django.urls import path
from .views import (SaleOrderCreate,
                    SaleList,
                    SaleCreate,
                    SaleDetailView,
                    SaleUpdateView,
                    get_item_price,generate_ticket_pdf
                    )
      
 
app_name="sale"

urlpatterns = [
    path('',SaleList.as_view(), name="sale-list"),
    path('add/', SaleOrderCreate.as_view(), name='sale_create'),
    path('detail/<int:id>', SaleDetailView.as_view(), name="sale-detail"),
    path('so/<int:id>/update', SaleUpdateView.as_view(), name='sale-update'),
    path('item-price/', get_item_price, name='item-price-api'),
    path('ticket/<int:sale_id>/pdf/', generate_ticket_pdf, name='generate_ticket_pdf'),
    
   
   
    
    ]