from django.urls import path
from .views import HomeView,login_user,logout_user
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Home
    path('', HomeView.as_view(), name='dashboard'),
    path('login/',login_user,name='login'),
    path('logout/', logout_user, name='logout'),  # Custom logout view
  

]
