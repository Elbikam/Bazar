from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("createCode",views.createBarcode, name='create barcode')
]