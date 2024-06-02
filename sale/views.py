from typing import Any
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import (
    CreateView, UpdateView
)
from .forms import (
    SaleForm,
    OrderForm,
    OrderFormSet
)
from .models import (
    Sale,Order
    )
from django.db import transaction
from django.urls import reverse_lazy

#//////////////////////////////////////////////////////////////////////

class SaleList(ListView):
    model = Sale
    queryset = Sale.objects.all()

class SaleCreate(CreateView):
    model = Sale
    fields = ['customer']



class SaleOrderCreate(CreateView):
    model = Sale
    fields = ['customer']
    success_url = reverse_lazy('sale-list')
   
    def get_context_data(self, **kwargs):
        data = super(SaleOrderCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['orders'] = OrderFormSet(self.request.POST)
            return data
        else:
            data['orders'] = OrderFormSet()
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        orders = context['orders']
        # print('orders',orders)
        with transaction.atomic():
            self.object = form.save()

            if orders.is_valid():
                orders.instance = self.object
                print(orders)

                return redirect('sale:sale-list')
            else:
                return self.render_to_response(self.get_context_data(form=form))
