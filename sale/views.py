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
from sale.forms import ( OrderForm,OrderFormSet,PersoneForm,SaleForm,
                        PaymentForm,CashForm,TicketForm)
from sale.models import Sale,Order,Payment,Cash,Persone
from stock.models import Item
from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from django.views.generic import View
import decimal
#//////////////////////////////////////////////////////////////////////
class SaleList(ListView):
    model = Sale

from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction
from .forms import PersoneForm, SaleForm, OrderFormSet, CashForm
from .models import Persone, Sale, Order, Payment
# /////////////////////////////////////////////////////////////////////////////////
def is_form_not_empty(form):
    return any(field.value() for field in form if field.name != 'DELETE')

def is_formset_not_empty(formset):
    return any(is_form_not_empty(form) for form in formset)
# //////////////////////////////////////////////////////////////////////////////////
class SaleOrderCreateView(View):
    template_name = 'sale/sale_form.html'  


    def get(self, request, *args, **kwargs):
        persone_form = PersoneForm()
        
        sale_form = SaleForm()
        orders = OrderFormSet()
        cash_form = CashForm()
        context = {
            'persone_form': persone_form,
            'sale_form': sale_form,
            'orders': orders,
            'cash_form': cash_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        persone_form = PersoneForm(request.POST)
        sale_form = SaleForm(request.POST, persone=persone_form.instance)

        # sale_form = SaleForm(request.POST)
        orders = OrderFormSet(request.POST)
        cash_form = CashForm(request.POST)

        if persone_form.is_valid() and sale_form.is_valid() and orders.is_valid() and cash_form.is_valid():
            with transaction.atomic():
                # Save the Person
                persone = persone_form.save()

                # Save the Sale
                sale = sale_form.save(commit=False)
                sale.customer = persone
                sale.save()
                
                # Save Orders              
                
                for order_form in orders:
                    if is_form_not_empty(order_form): 
                       order = order_form.save(commit=False)
                       order.so_id = sale
                       order.save()
                   

                # Save Payment
                payment = cash_form.save(commit=False)
                payment.sale_id = sale
                payment.save()
            
            return redirect('sale:sale-detail', pk=sale.pk)  # Redirect to the sale detail view

            
        # If form is not valid, re-render the form with errors
        context = {
            'persone_form': persone_form,
            'sale_form': sale_form,
            'orders': orders,
            'cash_form': cash_form,
        }
        return render(request, self.template_name, context)
                
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
    context_object_name = 'sale'  # This will be the name of the object in the template

def generate_ticket_pdf(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    context = {
        'sale': sale,
        'orders': sale.order_set.all(),
    }
    html_string = render_to_string('sale/sale_ticket.html', context)
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SO{sale_id}.pdf"'
    return response






