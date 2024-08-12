from django.urls import path
from .views import (SaleOrderCreateView,
                    SaleList,
                    SaleDetailView,
                    get_item_price,generate_ticket_pdf,
                
                    )
      
 
app_name="sale"

urlpatterns = [
    path('',SaleList.as_view(), name="sale-list"),
    path('add/', SaleOrderCreateView.as_view(), name='sale_create'),

    path('sale/<int:pk>', SaleDetailView.as_view(), name="sale-detail"),
    path('item-price/', get_item_price, name='item-price-api'),
    path('ticket/<int:sale_id>/pdf/', generate_ticket_pdf, name='generate_ticket_pdf'),
    
   
   
    
    ]