# dashboard/urls.py
from django.urls import path
from .views import DashboardView,MainPageView,mark_as_read

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('d/', MainPageView.as_view(), name='main_page'),
    path('notifications/mark-as-read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),

    
    
    
]
