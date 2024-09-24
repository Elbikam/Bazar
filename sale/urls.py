from django.urls import path
from . import views
from .views import (SaleCreateView,get_item_price,SaleDetailView,
                    DevisCreateView,DevisDetailView,generate_devis_pdf,VendorCreate,SaleVendorList,
                    SaleToVendorCreateView,SaleDetailView,generate_facture_pdf,generate_bonLivraison_pdf,
                    generate_sale_ticket,SaleToVendorDetails,
                    MonthlyPaymentView,VendorPaymentSummaryView,generate_recu,ReturnSaleCreateView,ReturnSaleDetails
                    
                
                    )
      
 
app_name="sale"

urlpatterns = [
    # Pesrone kind of customer
    path('order/', SaleCreateView.as_view(), name='order-create'),
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
    path('vendor/order/', SaleToVendorCreateView.as_view(), name='vendor-sale'),
    path('vendor/<int:pk>', views.SaleToVendorDetails, name='sale-vendor-detail'),
    path('vendor/facture/<int:sale_id>/pdf/', views.generate_facture_pdf, name='generate_facture_pdf'),
    path('vendor/bonLivraison/<int:sale_id>/pdf/', views.generate_bonLivraison_pdf, name='generate_bonlivraison_pdf'),

    # Monhtly Payment
    path('vendor/payment/', MonthlyPaymentView.as_view(), name='monthly-payment'),
    path('vendor/summary/<int:pk>/', views.VendorPaymentSummaryView, name='vendor-payment-summary'),
    path('vendor/recu/<int:vendor_id>/pdf/', views.generate_recu, name='generate_recu'),
    #Return Sale
    path('return_sale/', ReturnSaleCreateView.as_view(), name='return-create'),
    path('return/details/<int:pk>', views.ReturnSaleDetails, name='return-detail'),
   
    
    ]