from django.urls import path
from . import views
from .views import (SaleCreateView,get_item_price,SaleDetailView,generate_ticket_pdf,
                    DevisCreateView,DevisDetailView,generate_devis_pdf,VendorCreate,SaleVendorList,
                    SaleVendorCreateView,SaleVendorDetails,generate_facture_pdf,generate_bonLivraison_pdf,generate_sale_ticket,SaleReturnUpdateView

                
                    )
      
 
app_name="sale"

urlpatterns = [
    # Pesrone kind of customer
    path('order/', SaleCreateView.as_view(), name='sale-create'),
    path('order/item-price/', views.get_item_price, name='item-price-api'),
    path('order/<int:pk>', views.SaleDetailView, name='sale-detail'),
    path('ticket/<int:sale_id>/pdf/', views.generate_sale_ticket, name='generate_ticket_pdf'),
    # Devis
    path('devis/', DevisCreateView.as_view(), name='devis-create'),
    path('devis/<int:pk>', views.DevisDetailView, name='devis-detail'),
    path('devis_ticket/<int:devis_id>/pdf/', views.generate_devis_pdf, name='generate_devis_pdf'),
    # Vendor kind of customer
    path('vendor/', VendorCreate.as_view(), name='vendor-create'),
    path('vendor/list/', views.SaleVendorList, name='vendor-list'),
    path('vendor/sale/', SaleVendorCreateView.as_view(), name='vendor-sale'),
    path('vendor/<int:pk>', views.SaleVendorDetails, name='sale-vendor-detail'),
    path('vendor/facture/<int:sale_id>/pdf/', views.generate_facture_pdf, name='generate_facture_pdf'),
    path('vendor/bonLivraison/<int:sale_id>/pdf/', views.generate_bonLivraison_pdf, name='generate_bonlivraison_pdf'),
    # Sale return
    path('return/<int:pk>/', SaleReturnUpdateView.as_view(), name='sale-return'),


    
   
    
    ]