from django.db import transaction
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views.generic import ListView
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
    
)
from django.urls import reverse_lazy,reverse
from sale.forms import OrderFormSet,SaleForm,TicketForm
from sale.models import Sale,Order,Ticket
from stock.models import Item
from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string

#//////////////////////////////////////////////////////////////////////
class SaleList(ListView):
    model = Sale
  
class SaleCreate(CreateView):
    model = Sale
    fields = ['customer']
    

class SaleOrderCreate(CreateView):
    model = Sale
    fields = ['customer']
    # success_url = reverse_lazy('sale:sale-detail')
    
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
            else:
                return self.render_to_response(self.get_context_data(form=form))

            
          
                
def get_item_price(request):
    item_id = request.GET.get('item_id')
    try:
        item = Item.objects.get(id=int(item_id))
        price = item.price
    except Item.DoesNotExist:
        price = 0
    
    return JsonResponse({'price': price})       

class SaleDetailView(DetailView):
    model = Sale
    template_name = 'sale/sale_detail.html'
    context_object_name = 'sale'

    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Sale, id=id_)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        context['sale_orders'] = instance.order_set.all()
        return context



    
class SaleUpdateView(UpdateView):
    molde = Sale
    form_class = SaleForm
    template_name = 'sale/sale_update.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Sale, id=id_)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['orders'] = OrderFormSet(self.request.POST, instance=self.get_object())
        else:
            data['orders'] = OrderFormSet(instance=self.get_object())
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        orders = context['orders']
        with transaction.atomic():
            self.object = form.save()
            if orders.is_valid():
                orders.instance = self.object
                orders.save()
                return super().form_valid(form)
        return super().form_invalid(form)
    




def generate_ticket_pdf(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    context = {
        'sale': sale,
        'orders': sale.order_set.all(),
    }
    html_string = render_to_string('sale/ticket_template.html', context)
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SO{sale_id}.pdf"'
    return response






