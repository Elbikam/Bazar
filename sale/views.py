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
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError

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
        description = item.description
        return JsonResponse({'price': price,'description':description}) 
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

class SaleToVendorCreateView(View):
    template_name = 'sale/vendor_sale_form.html'  # template specific for vendor kind of customer

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

        if not (sale_to_vendor_form.is_valid() and orders.is_valid() and payment_form.is_valid()):
            # If any form is invalid, re-render the page with form errors
            context = {
                'sale_to_vendor_form': sale_to_vendor_form,
                'orders': orders,
                'payment_form': payment_form,
            }
            return render(request, self.template_name, context)

        # Wrap the following code in an atomic transaction to avoid partial saves
        with transaction.atomic():
            # Save the sale for the vendor
            saletovendor = sale_to_vendor_form.save(commit=False)
            saletovendor.save()

            # Process each order and update the item's stock
            for order_form in orders:
                if is_form_not_empty(order_form):
                    order = order_form.save(commit=False)
                    item = Item.objects.get(id=order.item_id)
                    if item.qte_inStock >= order.quantity:
                        item.qte_inStock -= order.quantity
                        item.save()
                        order.sale = saletovendor
                        order.save()
                    else:
                        raise ValidationError(f"Not enough stock for {item.name}.")

            #update vendor balance
            vendor = saletovendor.vendor
            vendor.balance -= saletovendor.get_TTC
            vendor.save()
            # Save the payment associated with the sale
            payment = payment_form.save(commit=False)
            payment.sale = saletovendor
            payment.save()

        return redirect('sale:sale-vendor-detail', pk=saletovendor.pk)


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

#////////////////////////////// Monthly Payment /////////////////////////////

class MonthlyPaymentView(View):
    template_name = 'sale/monthly_payment_form.html'

    def get(self, request, *args, **kwargs):
        monthly_payment_form = MonthlyPaymentForm()
        context = {
            'monthly_payment_form': monthly_payment_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        monthly_payment_form = MonthlyPaymentForm(request.POST)

        if monthly_payment_form.is_valid():
            with transaction.atomic():
                monthly_payment = monthly_payment_form.save(commit=False)

                vendor = monthly_payment_form.cleaned_data['vendor']
                amount_received = monthly_payment.amount_received
                vendor.balance += amount_received

                # Get the previous month and year
                now = timezone.now()
                last_month = now.month - 1 if now.month > 1 else 12
                last_month_year = now.year if now.month > 1 else now.year - 1

                # Fetch all unpaid sales for the previous month for the vendor
                unpaid_sales = SaleToVendor.objects.filter( vendor=vendor,date__month=last_month,date__year=last_month_year,payment__is_pay=False)

                # Calculate total amount to be paid for those sales
                total_due = sum(sale.get_TTC for sale in unpaid_sales)

                # Mark sales as paid and update vendor's balance
                for sale in unpaid_sales:
                    payment = Payment.objects.get(sale=sale)
                    payment.amount_received += sale.get_TTC
                    payment.is_pay = True
                    payment.save()
                    # Update vendor's balance
                    vendor.balance -= sale.get_TTC
                    vendor.save()
                # Vendor want to push some money
                vendor.save()

            # Redirect to a summary page showing vendor's updated balance
            return redirect('sale:vendor-payment-summary', pk=vendor.pk)
        else:
            context = {
            'monthly_payment_form': monthly_payment_form,
            }
            return render(request, self.template_name, context)


def VendorPaymentSummaryView(request, pk):

    vendor = get_object_or_404(Vendor, pk=pk)
    # monthly_amount_received
     
    now = timezone.now()
    last_month = now.month - 1 if now.month > 1 else 12
    last_month_year = now.year if now.month > 1 else now.year - 1
    # Fetch all unpaid sales for the previous month for the vendor
    paid_sales = SaleToVendor.objects.filter( vendor=vendor,date__month=last_month,date__year=last_month_year,payment__is_pay=True)
    # total_amount_received = payment.amount_received for payment in vendor.saletovendor_set.all()
    total_amount_paid = sum(sale.get_TTC for sale in paid_sales)
    context = {
        'vendor': vendor,
        'paid_sales': paid_sales,
        'total_amount_paid':total_amount_paid,
        'last_month': last_month,
        'last_month_year': last_month_year,
    }
    return render(request, 'sale/vendor_payment_summary.html', context)
                    

def generate_recu(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    now = timezone.now()
    date = now
    last_month = now.month - 1 if now.month > 1 else 12
    last_month_year = now.year if now.month > 1 else now.year - 1
    paid_sales = SaleToVendor.objects.filter( vendor=vendor,date__month=last_month,date__year=last_month_year,payment__is_pay=True)
    total_amount_paid = sum(sale.get_TTC for sale in paid_sales)
    context = {
        'company_info': {
            'name': 'Nina Bazar',
            'info': 'RC1021 ICE:001680586000002 PATENTE:49659021',
            'address': 'AV YOUSSEF BEN TACHFINE N138 GUELMIM',
            'phone': '06 72 38 17 47'
        },
        'vendor': vendor,
        'paid_sales': paid_sales,
        'total_amount_paid':total_amount_paid,
        'last_month': last_month,
        'last_month_year': last_month_year,
        'date':date,
    }
    # Render the reciep template with sale details
    html_string = render_to_string('sale/recu_payment.html', context)
    html = HTML(string=html_string,base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="R{vendor.pk}.pdf"'
    return response                   

#///////////////// return Sale /////////////////////////////////
class ReturnSaleCreateView(View):
    template_name = 'sale/return_sale_form.html'  

    def get(self, request, *args, **kwargs):       
        return_sale_form = ReturnSaleForm()
        orders = ReturnFormSet()
        context = {
            'return_sale_form': return_sale_form,
            'orders': orders,
           
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        return_sale_form = ReturnSaleForm(request.POST)
        orders = ReturnFormSet(request.POST)
        if return_sale_form.is_valid() and orders.is_valid():
            try:
                with transaction.atomic():
                    # Save the Sale
                    return_sale = return_sale_form.save(commit=False)
                    sale = Sale.objects.get(id=return_sale.so)
                    return_sale.sale = sale
                    return_sale.save()
                    
                    # Save Orders              
                    for order_form in orders:
                        if is_form_not_empty(order_form): 
                            order = order_form.save(commit=False)
                            try:
                                item = Item.objects.get(id=order.item_id)
                            except Item.DoesNotExist:
                                order_form.add_error(None, 'Item does not exist')
                                raise

                            item.qte_inStock += order.quantity
                            item.save()
                            order._sale= return_sale
                            order.save()


                return redirect('sale:return-detail', pk=return_sale.pk)  # Redirect to the sale detail view

            except Exception as e:
                # Log the exception for debugging if necessary
                print(f"Error saving sale: {e}")
                
        # If form is not valid or an exception occurs, re-render the form with errors
        context = {
            'return_sale_form': return_sale_form,
            'orders': orders,
        }
        return render(request, self.template_name, context)
    


def ReturnSaleDetails(request,pk):
    return_sale = get_object_or_404(ReturnSale, pk=pk)
    return render(request, 'sale/return_sale_details.html', {'return_sale': return_sale})