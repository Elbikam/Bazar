from django.db import transaction
from django.views.generic import ListView
from django.views.generic.edit import (
    CreateView,
    
)
from django.urls import reverse_lazy
from sale.forms import OrderFormSet
from .models import Sale
#//////////////////////////////////////////////////////////////////////
class SaleList(ListView):
    model = Sale
  
class SaleCreate(CreateView):
    model = Sale
    fields = ['phone']
    

class SaleOrderCreate(CreateView):
    model = Sale
    fields = ['phone']
    # success_url = reverse_lazy("sale-list")

    def get_context_data(self, **kwargs):
        data = super(SaleOrderCreate,self).get_context_data(**kwargs)
        if self.request.POST:
            data['orders'] = OrderFormSet(self.request.POST)
            
        else:
            data['orders'] = OrderFormSet()
        return data    
       
          
    def form_valid(self, form):
       context = self.get_context_data()
       orders = context['orders']
       with transaction.atomic():
           self.object = form.save()
           if orders.is_valid():
               orders.instance = self.object

               orders.save()
       return super(SaleOrderCreate,self).form_valid(form)    

           
       
       
            

