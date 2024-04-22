from django.urls import path

from stock.views import (
    ItemCreateView,
    ItemListView,
    ItemDetailView,
    ItemUpdateView,
    ItemDeleteView,
    
)


app_name="stock"

urlpatterns = [
    
     path('',ItemListView.as_view(), name= 'item-list'),
     path('create/', ItemCreateView.as_view(), name='item-create'),
     path('<int:pk>/update', ItemUpdateView.as_view(), name='item-update'),
     path('<int:id>/', ItemDetailView.as_view(), name="item-detail"),
     path('<int:id>/delete/', ItemDeleteView.as_view(), name='item-delete'),

    
 
]