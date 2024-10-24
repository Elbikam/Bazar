from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from sale.models import *
from django.db.models import Sum
from stock.models import Notification
from django.db.models import Q  # Import Q for complex queries

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sales'] = Sale.objects.count()
        context['total_orders'] = Order_Line.objects.count()
        context['total_revenue'] = Order_Line.objects.aggregate(total_revenue=Sum('price'))['total_revenue']
        context['recent_sales'] = Sale.objects.order_by('-date')[:5]
        return context


class MainPageView(TemplateView):
    template_name = 'dashboard/main_page.html'


# Dashboard view with notifications
def dashboard_view(request):
    notifications = Notification.objects.filter(read=False).order_by('-created_at')[:5]
    notifications_count = notifications.count()

    context = {
        'notifications': notifications,
        'notifications_count': notifications_count,
        'total_sales': Sale.objects.count(),
        'total_orders': Order_Line.objects.count(),
        'total_revenue': Order_Line.objects.aggregate(total_revenue=Sum('price'))['total_revenue'],
        'recent_sales': Sale.objects.order_by('-date')[:5]
    }
    return render(request, 'dashboard/dashboard.html', context)



from django.shortcuts import get_object_or_404

def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.read = True
    notification.save()
    return redirect('dashboard:dashboard')








