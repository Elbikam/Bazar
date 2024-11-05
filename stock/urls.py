from django.urls import path

from django.urls import path
from .views import (ItemCreateView,  ReceiptCreateView,
                   ItemListView,
                   stock_alert_view,StockAlertCreateView,
                   AlertSuccessView,filter_items,
                    fetch_items,ReceiptListView,ReceiptDetailView, search_item_in_stock
                   
                   )

app_name = 'stock'


urlpatterns = [
    #Item 
    path('item/create/', ItemCreateView.as_view(), name='create_item'),
    path('receipt/', ReceiptCreateView.as_view(), name='create_receipt'),
    path('items/', ItemListView.as_view(), name='item_list'),
    path('stock-alerts/', stock_alert_view, name='stock_alerts'),
    path('alerts/', StockAlertCreateView.as_view(), name='create_alert'),
    path('alert/success/', AlertSuccessView.as_view(), name='alert_success'),  # Add this line
    path('filter-items/', filter_items, name='filter_items'),
    path('fetch-items/', fetch_items, name='fetch_items'),
    path('receipt/list', ReceiptListView.as_view(), name='receipt_list'),  # Receipt list view
    path('receipt/detail/<int:pk>/', ReceiptDetailView.as_view(), name='receipt-detail'),  # Receipt detail view
    # Search
    path('search/', search_item_in_stock, name='search_item'),
]

    