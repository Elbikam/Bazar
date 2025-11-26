from django.urls import path
from . import views
from django.urls import path
from .views import (TheCreateView,  ReceiptCreateView,
                   TheListView,
                   stock_alert_view,StockAlertCreateView,
                   AlertSuccessView,filter_items,
                    fetch_items,ReceiptListView,ReceiptDetailView, search_item_in_stock,get_item_quantity
                   
                   )

app_name = 'stock'


urlpatterns = [
    #Item 
    path('the/create/', TheCreateView.as_view(), name='create_the'),
    path('receipt/', ReceiptCreateView.as_view(), name='create_receipt'),
    path('items/', TheListView.as_view(), name='the_list'),
    path('stock-alerts/', stock_alert_view, name='stock_alerts'),
    path('alerts/', StockAlertCreateView.as_view(), name='create_alert'),
    path('alert/success/', AlertSuccessView.as_view(), name='alert_success'),  # Add this line
    path('filter-items/', filter_items, name='filter_items'),
    path('fetch-items/', fetch_items, name='fetch_items'),
    path('receipt/list', ReceiptListView.as_view(), name='receipt_list'),  # Receipt list view
    path('receipt/detail/<int:pk>/', ReceiptDetailView.as_view(), name='receipt-detail'),  # Receipt detail view

    # Search
    path('search/', search_item_in_stock, name='search_item'),
    path('ai/', views.get_item_quantity, name='get_item_quantity'),
    path('test-function-calling/', views.test_function_calling, name='test_function_calling'),

]

    