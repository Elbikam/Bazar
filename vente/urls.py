from django.urls import path
from . import views

app_name="vente"

urlpatterns = [
    path("", views.index, name="index"),
    path("order/", views.add_order, name="add order"),
        
]