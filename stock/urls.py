from django.urls import path
from .views import ( ItemCreate,ItemDetailView,TheDetailView,TheCreate,
                    ParfumCreate,ParfumDetailView,item_search,
                    alert_stock
                    )
from . import views
app_name = 'stock'

urlpatterns = [

    #Item
    path('item/',ItemCreate.as_view(),name='item-create'),
    path('detail/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('search/', item_search, name='item-search'),
    path('alert/', alert_stock, name='alert'),

    #The
    path('the/',TheCreate.as_view(),name='the-create'),
    path('detail/<int:pk>/', TheDetailView.as_view(), name='the-detail'),

    #Parfum
    path('parfum/',ParfumCreate.as_view(),name='parfum-create'),
    path('detail/<int:pk>/', ParfumDetailView.as_view(), name='parfum-detail'),


    
    ]