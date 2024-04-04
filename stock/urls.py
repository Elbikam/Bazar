from django.urls import path
from . import views

app_name="stock"

urlpatterns = [
    path("", views.index, name="index"),
    path("the/",views.add_The, name="The"),
    path("search/",views.search_view, name='search'),
    path("parfum/",views.add_Parfum,name="Parfum")
    
]