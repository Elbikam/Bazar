from django.urls import path

from stock.views import (
    ItemListView,
    TheCreateView,
    TheListView,
    #TheDetailView,
    TheUpdateView,
    ItemDeleteView,
    #parfum
    ParfumCreateView,
    #ParfumDetailView,
    ParfumListView,
    ParfumUpdateView,
    ItemDetailView
)

app_name="stock"

urlpatterns = [
    #Item
    path('<int:id>/', ItemDetailView.as_view(), name="item-detail"),
    path('<int:id>/delete/', ItemDeleteView.as_view(), name='the-delete'),
    #The
    path('',ItemListView.as_view(), name= 'item-list'),
    path('thelist/',TheListView.as_view(), name= 'the-list'),
    path('the/', TheCreateView.as_view(), name='the-create'),
    path('<int:id>/update', TheUpdateView.as_view(), name='the-update'),
    #path('<int:id>/', TheDetailView.as_view(), name="the-detail"),
    path('<int:id>/delete/', ItemDeleteView.as_view(), name='the-delete'),
    #PARFUM
    path('parfum/', ParfumCreateView.as_view(), name='parfum-create'),
    # path('parfumlist/',ParfumListView.as_view(), name= 'parfum-list'),
    # path('<int:id>/', ParfumDetailView.as_view(), name="parfum-detail"),
    path('parfumlist/',ParfumListView.as_view(), name= 'parfum-list'),
    path('<int:id>/update', ParfumUpdateView.as_view(), name='parfum-update'),

   
]