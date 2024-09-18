from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from decimal import Decimal, InvalidOperation,getcontext
from sale.forms import *
from sale.models import *
from stock.models import *
from django.shortcuts import render, redirect
from django.views.generic import View
from django.db import transaction
from weasyprint import HTML
from django.templatetags.static import static
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import (UpdateView)
from django.http import HttpResponseRedirect

#////////////////////////////// Function check is empty form ///////////////////////////////////////
def is_form_not_empty(form):
    return any(field.value() for field in form if field.name != 'DELETE')

def is_formset_not_empty(formset):
    return any(is_form_not_empty(form) for form in formset)

#/////////////////////////// Sale ///////////////////////////////////////////
class SaleCreateView(View):
    template_name = 'sale/order_form.html'  

    def get(self, request, *args, **kwargs):       
        sale_form = SaleForm()
        orders = OrderFormSet()
        payment_form = PaymentForm()
        context = {
            'sale_form': sale_form,
            'orders': orders,
            'payment_form': payment_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        sale_form = SaleForm(request.POST)
        orders = OrderFormSet(request.POST)
        payment_form = PaymentForm(request.POST)

        if sale_form.is_valid() and orders.is_valid() and payment_form.is_valid():
            try:
                with transaction.atomic():
                    # Save the Sale
                    sale = sale_form.save(commit=False)
                    sale.save()

                    # Save Orders              
                    for order_form in orders:
                        if is_form_not_empty(order_form): 
                            order = order_form.save(commit=False)
                            try:
                                item = Item.objects.get(id=order.item_id)
                            except Item.DoesNotExist:
                                order_form.add_error(None, 'Item does not exist')
                                raise

                            item.qte_inStock -= order.quantity
                            item.save()
                            order.sale= sale
                            order.save()

                    # Save Payment
                    payment = payment_form.save(commit=False)
                    payment.sale = sale
                    payment.save()

                return redirect('sale:sale-detail', pk=sale.pk)  # Redirect to the sale detail view

            except Exception as e:
                # Log the exception for debugging if necessary
                print(f"Error saving sale: {e}")
                
        # If form is not valid or an exception occurs, re-render the form with errors
        context = {
            'sale_form': sale_form,
            'orders': orders,
            'payment_form': payment_form,
        }
        return render(request, self.template_name, context)

                
def get_item_price(request):
    item_id = request.GET.get('item_id')
    try:
        item = Item.objects.get(id=int(item_id))
        price = item.price
        return JsonResponse({'price': price}) 
    except Item.DoesNotExist:
        return JsonResponse({'price': None})
    

def SaleDetailView(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sale/order_detail.html', {'sale': sale})

# ////////////////// Ticket PDF ////////////////////////////////
def generate_sale_ticket(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Gather all the necessary data for the ticket
    context = {
        'company_info': {
            'name': 'Nina Bazar',
            'info': 'RC1021 ICE:001680586000002 PATENTE:49659021',
            'address': 'AV YOUSSEF BEN TACHFINE N138 GUELMIM',
            'phone': '06 72 38 17 47'
        },
        'sale': sale,
        'items': sale.order_line_set.all(),  # Retrieve related inline orders
        'total_items': sale.total_of_items,
        'static_url': request.build_absolute_uri(static('')),
        'HT_total': sale.get_HT,
        'TVA_total': sale.get_TVA,
        'TTC_total': sale.get_TTC,
        
       
    }

    # Render the ticket template with sale details
    html_string = render_to_string('sale/ticket.html', context)
    html = HTML(string=html_string,base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="SO{sale_id}.pdf"'
    return response
#/////////////////////////////// Devis /////////////////////////////////
class DevisCreateView(View):
    template_name = 'sale/devis_form.html'  

    def get(self, request, *args, **kwargs):      
        devis_form = DevisForm()
        orders = DOrderFormSet()
        context = {
            'devis_form': devis_form,
            'orders': orders,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        devis_form = DevisForm(request.POST)
        orders = DOrderFormSet(request.POST)
        if devis_form.is_valid() and orders.is_valid():
            with transaction.atomic():
                # Save the Sale
                devis = devis_form.save(commit=False)
                devis.save()

                # Save Orders              
                for order_form in orders:
                    if is_form_not_empty(order_form): 
                       order = order_form.save(commit=False)
                       order.devis = devis
                       order.save()

            
            return redirect('sale:devis-detail', pk=devis.pk)  # Redirect to the sale detail view
        
        context = {
            'devis_form': devis_form,
            'orders': orders,
        }
        return render(request, self.template_name, context)
                

def DevisDetailView(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    return render(request, 'sale/devis_detail.html', {'devis': devis})
#///////////////////////////// Devis PDF /////////////////////////////
def generate_devis_pdf(request, devis_id):
    devis = get_object_or_404(Devis, id=devis_id)
    context = {
        'devis': devis,
        'orders': devis.devis_line_set.all(),
        'static_url': request.build_absolute_uri(static('')),
    }
    html_string = render_to_string('sale/devis_ticket.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    # Return the PDF as an attachment
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SD{devis_id}.pdf"'
    return response

# ////////////////////////////////////// Vendor //////////////////////////////////////
class VendorCreate(View):
    template_name = 'sale/vendor_form.html'

    def get(self, request, *args, **kwargs):
        vendor_form = VendorForm()

        context = {
            'vendor_form': vendor_form,
        }
        return render(request, self.template_name, context)
    def post(self, request, *args, **kwargs):
        vendor_form = VendorForm(request.POST)
        if vendor_form.is_valid():
            vendor_form.save()

            return redirect('sale:vendor-list')
        context = {
            'vendor_form': vendor_form,
        }
        return render(request, self.template_name, context)
   

def safe_decimal_conversion(value):
        return Decimal(value or '0.00')


class SaleVendorCreateView(View):
    template_name = 'sale/vendor_sale_form.html' # this template specific  for vendor kind of customer 

    def get(self, request, *args, **kwargs):
        sale_to_vendor_form = SaleToVendorForm()
        orders = OrderFormSet()
        payment_form = PaymentForm()
        context = {
            'sale_to_vendor_form': sale_to_vendor_form,
            'orders': orders,
            'payment_form': payment_form,
        }
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        sale_to_vendor_form = SaleToVendorForm(request.POST)
        orders = OrderFormSet(request.POST)
        payment_form = PaymentForm(request.POST)

        if sale_to_vendor_form.is_valid() and orders.is_valid() and payment_form.is_valid():
                with transaction.atomic():                    
                    # Process sale_vendor, orders, and payments                    
                    saletovendor = sale_to_vendor_form.save(commit=False)
                    saletovendor.save()

                    for order_form in orders:
                        if is_form_not_empty(order_form):
                            order = order_form.save(commit=False)
                            order.order = saletovendor
                            item = Item.objects.get(id=order.item_id)
                            item.qte_inStock -= order.quantity
                            item.save()
                            order.sale = saletovendor
                            order.save()

                    payment = payment_form.save(commit=False)
                    payment.sale = saletovendor
                    payment.save()

                return redirect('sale:sale-vendor-detail', pk=saletovendor.pk)

        context = {
            'sale_to_vendor_form': sale_to_vendor_form,
            'orders': orders,
            'payment_form': payment_form,
        }
        return render(request, self.template_name, context)
    
def SaleToVendorDetails(request, pk):
    sale_to_vendor = get_object_or_404(SaleToVendor, pk=pk)
    return render(request, 'sale/vendor_order_detail.html', {'sale_to_vendor': sale_to_vendor}) 

def SaleVendorList(request):
   vendors = Vendor.objects.all()
   return render(request, 'sale/vendor_list.html', {'vendors': vendors}) 


#//////////////////////////////////// Facture ////////////////////////////////
def generate_facture_pdf(request, sale_id):
    sale_to_vendor = get_object_or_404(SaleToVendor, id=sale_id)
    context = {
        'sale_to_vendor': sale_to_vendor,
        'orders': sale_to_vendor.order_line_set.all(),
        'static_url': request.build_absolute_uri(static('')),
        'company_info': {
            'name': 'Nina Bazar',
            'info': 'RC1021 ICE:001680586000002 PATENTE:49659021',
            'address': 'AV YOUSSEF BEN TACHFINE N138 GUELMIM',
            'phone': '06 72 38 17 47'
        },
        # 'barcode':generate_barcode(sale_vendor.id),

    }

    html_string = render_to_string('sale/facture.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    # Return the PDF as an attachment
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SOF{sale_id}.pdf"'
    return response
#/////////////////////////////////// Bon Livraison ////////////////////////////////
def generate_bonLivraison_pdf(request, sale_id):
    sale_to_vendor = get_object_or_404(SaleToVendor, id=sale_id)
    context = {
        'sale_to_vendor': sale_to_vendor,
        'orders': sale_to_vendor.order_line_set.all(),
        'static_url': request.build_absolute_uri(static('')),
    }
    html_string = render_to_string('sale/bonLivraison.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    # Return the PDF as an attachment
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BL{sale_id}.pdf"'
    return response

# ////////////////////////////////////// Sale Return ////////////////////////////////
class OrderReturnUpdateView(UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sale/sale_return.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['orders'] = OrderFormSet(self.request.POST, instance=self.object)
            context['payment_form'] = PaymentForm(self.request.POST, instance=self.object.cash)
        else:
            context['orders'] = OrderFormSet(instance=self.object)
            context['payment_form'] = PaymentForm(instance=self.object.cash)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orders = context['orders']
        payment_form = context['payment_form']

        if form.is_valid() and orders.is_valid() and payment_form.is_valid():
            with transaction.atomic():
                refund_amount = 0
                for order_form in orders.deleted_forms:
                   if is_form_not_empty(order_form):
                        order = order_form.save(commit=False)
                        refund_amount += order.get_subtotal
                        item = Item.objects.get(id=order.item.id)
                        item.qte_inStock += order.quantity  # Increase stock as items are returned
                        item.save()
                        order.delete()
          
            return redirect('sale:sale-return-detail', pk=self.object.pk)
        
        return self.render_to_response(self.get_context_data(form=form))
def SaleReturnDetail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sale/return_detail.html', {'sale': sale})











