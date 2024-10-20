from django.shortcuts import render
from django.views.generic import TemplateView
from sale.models import *
from django.db.models import Sum

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
