from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("the/",views.add_item, name="add_item"),
    path("list/",views.list, name="list")
]