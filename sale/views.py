from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from decimal import Decimal, InvalidOperation,getcontext
from sale.forms import SaleForm,VendorForm,VendorSaleForm,OrderFormSet,CashForm,DOrderFormSet,DevisForm,InlineDevis
from sale.models import *
from stock.models import *
from django.shortcuts import render, redirect
from django.views.generic import View
from django.db import transaction
from weasyprint import HTML
from django.templatetags.static import static
from django.http import HttpResponse
from django.conf import settings
# from barcode import Code128,ImageWriter



#////////////////////////////// Function check is empty form ///////////////////////////////////////
def is_form_not_empty(form):
    return any(field.value() for field in form if field.name != 'DELETE')

def is_formset_not_empty(formset):
    return any(is_form_not_empty(form) for form in formset)

#/////////////////////////// Sale ///////////////////////////////////////////
class SaleCreateView(View):
    template_name = 'sale/sale_form.html'  

    def get(self, request, *args, **kwargs):       
        sale_form = SaleForm()
        orders = OrderFormSet()
        cash_form = CashForm()
        context = {
            'sale_form': sale_form,
            'orders': orders,
            'cash_form': cash_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        sale_form = SaleForm(request.POST)
        orders = OrderFormSet(request.POST)
        cash_form = CashForm(request.POST)

        if sale_form.is_valid() and orders.is_valid() and cash_form.is_valid():
            with transaction.atomic():
                # Save the Sale
                sale = sale_form.save(commit=False)
                sale.save()

                # Save Orders              
                for order_form in orders:
                    if is_form_not_empty(order_form): 
                       order = order_form.save(commit=False)
                       order.sale = sale
                       item = order.item_id
                       item = Item.objects.get(id=item)
                       item.qte_inStock -= order.quantity
                       item.save()
                       order.save()
                   

                # Save Payment
                payment = cash_form.save(commit=False)
                payment.sale = sale
                payment.save()
            
            return redirect('sale:sale-detail', pk=sale.pk)  # Redirect to the sale detail view

            
        # If form is not valid, re-render the form with errors
        context = {
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
        return JsonResponse({'price': price}) 
    except Item.DoesNotExist:
        return JsonResponse({'price': None})
    

def SaleDetailView(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sale/sale_detail.html', {'sale': sale})

# ////////////////// Ticket PDF ////////////////////////////////
def generate_ticket_pdf(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Adding static URL to the context
    context = {
        'sale': sale,
        'orders': sale.inlineorder_set.all(),
        'static_url': request.build_absolute_uri(static('')),
    }
    
    # Render the template with the context
    html_string = render_to_string('sale/ticket.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    # Return the PDF as an attachment
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SO{sale_id}.pdf"'
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
        'orders': devis.inlinedevis_set.all(),
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
        sale_vendor_form = VendorSaleForm()
        orders = OrderFormSet()
        cash_form = CashForm()
        context = {
            'sale_vendor_form': sale_vendor_form,
            'orders': orders,
            'cash_form': cash_form,
        }
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        sale_vendor_form = VendorSaleForm(request.POST)
        orders = OrderFormSet(request.POST)
        cash_form = CashForm(request.POST)

        if sale_vendor_form.is_valid() and orders.is_valid() and cash_form.is_valid():
                with transaction.atomic():                    
                    # Process sale_vendor, orders, and payments                    
                    sale_vendor = sale_vendor_form.save(commit=False)
                    sale_vendor.save()

                    for order_form in orders:
                        if is_form_not_empty(order_form):
                            order = order_form.save(commit=False)
                            order.sale = sale_vendor
                            item = Item.objects.get(id=order.item_id)
                            item.qte_inStock -= order.quantity
                            item.save()
                            order.save()

                    payment = cash_form.save(commit=False)
                    payment.sale = sale_vendor
                    payment.save()

                return redirect('sale:sale-vendor-detail', pk=sale_vendor.pk)

        context = {
            'sale_vendor_form': sale_vendor_form,
            'orders': orders,
            'cash_form': cash_form,
        }
        return render(request, self.template_name, context)
    
def SaleVendorDetails(request, pk):
    sale_vendor = get_object_or_404(Sale_Vendor, pk=pk)
    return render(request, 'sale/vendor_sale_detail.html', {'sale_vendor': sale_vendor}) 

def SaleVendorList(request):
   vendors = Vendor.objects.all()
   return render(request, 'sale/vendor_list.html', {'vendors': vendors}) 
#////////////////////////////////// Barcode ////////////////////////////////////
# def generate_barcode(data):
#     code = Code128(data, writer=ImageWriter())
#     return code.save("barcode.png")


#//////////////////////////////////// Facture ////////////////////////////////
def generate_facture_pdf(request, sale_id):
    sale_vendor = get_object_or_404(Sale_Vendor, id=sale_id)
    context = {
        'sale_vendor': sale_vendor,
        'orders': sale_vendor.inlineorder_set.all(),
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
    sale_vendor = get_object_or_404(Sale_Vendor, id=sale_id)
    context = {
        'sale_vendor': sale_vendor,
        'orders': sale_vendor.inlineorder_set.all(),
        'static_url': request.build_absolute_uri(static('')),
    }
    html_string = render_to_string('sale/bonLivraison.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    # Return the PDF as an attachment
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BL{sale_id}.pdf"'
    return response
#/////////////////////////////////////// Generate PDF //////////////////////////////
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
        'items': sale.inlineorder_set.all(),  # Retrieve related inline orders
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


