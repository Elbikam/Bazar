from django.db import transaction
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views.generic import ListView
from django.views.generic import (
    CreateView,
    DetailView,
    
)
from django.urls import reverse_lazy
from sale.forms import OrderFormSet
from sale.models import Sale,Order
from stock.models import Item
from django.shortcuts import render, get_object_or_404
#//////////////////////////////////////////////////////////////////////
class SaleList(ListView):
    model = Sale
  
class SaleCreate(CreateView):
    model = Sale
    fields = ['phone']
    

class SaleOrderCreate(CreateView):
    model = Sale
    fields = ['phone']
    
    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['orders'] = OrderFormSet(self.request.POST)
        else:
            data['orders'] = OrderFormSet()
        return data
    

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        context = self.get_context_data()
        orders = context['orders']
        with transaction.atomic():
            self.object = form.save()
            if orders.is_valid():
                orders.instance = self.object
                orders.save()
                return super().form_valid(form)
                
       

class SaleDetailView(DetailView):
    model = Sale
    

    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Sale, id=id_)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        context['sale_orders'] = instance.order_set.all()
        return context



    
    


   