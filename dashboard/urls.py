from django.urls import path
from .views import HomeView,login_user,logout_user,ai_report_generator,ai_report_the_inventory,generate_sales_report_view
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Home
    path('', HomeView.as_view(), name='dashboard'),
    path('login/',login_user,name='login'),
    path('logout/', logout_user, name='logout'),  # Custom logout view
    #AI report
    path('report_ai/', ai_report_generator, name='report_ai'),
    path('the_ai_report/', ai_report_the_inventory, name='the_ai_report'),
    path('inventory_report/', views.inventory_report, name='inventory_report'),
    path('sales_report/', generate_sales_report_view, name='sales_report'),
   
]
  


