# dashboard/urls.py
from django.urls import path
from .views import DashboardView,MainPageView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('d/', MainPageView.as_view(), name='main_page'),
   
  

    
    
    
]
