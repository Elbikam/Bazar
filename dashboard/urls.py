from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views 

app_name = 'dashboard'

urlpatterns = [
    # Home
    path('', HomeView.as_view(), name='dashboard'),
    path('login/',login_user,name='login'),
    path('logout/', logout_user, name='logout'),  # Custom logout view
    path('ai_report',GenerateReport.as_view(),name='ai_report'),
    path('chat_api/', views.chat_api, name='chat_api'),
    path('chat_page',ChatView.as_view(),name='chat_page'),
    path('agent/', dashboard, name='agent_dashboard'),
    path('agent/chat/', chat_api, name='agent_chat'),
]
  


