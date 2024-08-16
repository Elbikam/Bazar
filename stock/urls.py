from django.urls import path

from stock.views import (
    #Item
    ItemListView,
    ItemDetailView,
    ItemDeleteView,
    alert_stock,
    #The
    TheCreateView,
    TheListView,
    TheUpdateView,
    TheDetailView,
    #parfum
    ParfumCreateView,
    ParfumDetailView,
    ParfumListView,
    ParfumUpdateView,
    item_search
  
)


app_name="stock"

urlpatterns = [
    #Item
    path('<int:id>/', ItemDetailView.as_view(), name="item-detail"),
    path('<int:id>/delete/', ItemDeleteView.as_view(), name='the-delete'),
    path('alert/',view=alert_stock, name="alert"),
    path('search/', item_search, name='item_search'),
    #The
    path('',ItemListView.as_view(), name= 'item-list'),
    path('thelist/',TheListView.as_view(), name= 'the-list'),
    path('the/', TheCreateView.as_view(), name='create-the'),
    path('the/<int:id>/update', TheUpdateView.as_view(), name='the-update'),
    path('the/<int:id>', TheDetailView.as_view(), name="the-detail"),
    #PARFUM
    path('parfum/', ParfumCreateView.as_view(), name='create-parfum'),
    path('parfumlist/',ParfumListView.as_view(), name= 'parfum-list'),
    path('parfum/<int:id>', ParfumDetailView.as_view(), name="parfum-detail"),
    path('parfum/<int:id>/update', ParfumUpdateView.as_view(), name='parfum-update'),

   
]