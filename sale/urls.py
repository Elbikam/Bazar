from django.urls import path
from . import views
from .views import (SaleCreateView,get_item_price, SaleDetailView,
                    DevisCreateView,DevisDetailView,generate_devis_pdf,DealerCreate,SaleDealerList,
                    SaleToDealerCreateView,SaleDetailView,generate_facture_pdf,generate_bonLivraison_pdf,
                    generate_sale_ticket,SaleToDealerDetails,
                    MonthlyPaymentCreateView,MonthlyPaymentDetails,generate_recu,RefundCreateView,RefundDetails,
                    BalanceLimitErrorView,DealerBlockedErrorView,RefundDealerCreateView,RefundDealerDetails,
                    generate_refund,generate_sale_ticket_to_dealer
                    
                
                    )
      
 
app_name="sale"

urlpatterns = [
    # Pesrone kind of customer
    path('order/', SaleCreateView.as_view(), name='order-create'),
    path('order/item-price/', views.get_item_price, name='item-price-api'),
    path('order/<int:pk>', views.SaleDetailView, name='sale-detail'),
    path('ticket/<int:sale_id>/pdf/', views.generate_sale_ticket, name='generate_ticket_pdf'),
    # # Devis
    path('devis/', DevisCreateView.as_view(), name='devis-create'),
    path('devis/<int:pk>', views.DevisDetailView, name='devis-detail'),
    path('devis_ticket/<int:devis_id>/pdf/', views.generate_devis_pdf, name='generate_devis_pdf'),
    # # Dealer kind of customer
    path('dealer/', DealerCreate.as_view(), name='dealer-create'),
    path('dealer/list/', views.SaleDealerList, name='dealer-list'),
    path('dealer/order/', SaleToDealerCreateView.as_view(), name='dealer-sale'),
    path('dealer/<int:pk>', views.SaleToDealerDetails, name='sale-dealer-detail'),
    path('dealer/facture/<int:sale_id>/pdf/', views.generate_facture_pdf, name='generate_facture_pdf'),
    path('dealer/bonLivraison/<int:sale_id>/pdf/', views.generate_bonLivraison_pdf, name='generate_bonlivraison_pdf'),
    path('balance-limit-error/', BalanceLimitErrorView.as_view(), name='balance-limit-error'),
    path('dealer-blocked-error/', DealerBlockedErrorView.as_view(), name='dealer-blocked-error'),
    path('dealer/ticket/<int:sale_id>/pdf/', views.generate_sale_ticket_to_dealer, name='generate_ticket_dealer_pdf'),


    
   

    # # Monhtly Payment
    path('dealer/payment/',MonthlyPaymentCreateView.as_view(), name='monthly-payment-create'),
    path('monthly_payment/<int:pk>/', views.MonthlyPaymentDetails, name='monthly-payment'),
    path('payment/recu/<int:payment_id>/pdf/', views.generate_recu, name='generate_recu'),
    # #Refund
    path('refund', RefundCreateView.as_view(), name='refund-create'),
    path('refund/details/<int:pk>', views.RefundDetails, name='refund-detail'),
    path('refund/dealer', RefundDealerCreateView.as_view(), name='refund-dealer-create'),
    path('refund/payment/<int:pk>', views.RefundDealerDetails, name='refund-dealer-payment'),
    path('refund/generate/<int:refund_id>/pdf/', views.generate_refund, name='generate_refund'),
    
]