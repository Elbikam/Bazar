from django.db import transaction
from django.views.generic import ListView
from django.views.generic.edit import (
    CreateView,
    
)
from django.urls import reverse_lazy
from sale.forms import OrderFormSet
from .models import Sale
from stock.models import Item
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
                
       

     
       

            
      

        
    
    


   