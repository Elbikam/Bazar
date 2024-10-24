from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.views.generic import ListView
from decimal import Decimal, InvalidOperation,getcontext
from sale.forms import *
from sale.models import *
from stock.models import *
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
from datetime import timedelta
from django.http import JsonResponse
from django.views.generic import TemplateView
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
        payment_form = CashPaymentForm()
        context = {
            'sale_form': sale_form,
            'orders': orders,
            'payment_form': payment_form,
        }
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        sale_form = SaleForm(request.POST)
        orders = OrderFormSet(request.POST)
        payment_form = CashPaymentForm(request.POST)

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

                            # Check if the item exists and retrieve the stock
                            try:
                                item = Stock.objects.get(item_id=order.item.item)
                            except Stock.DoesNotExist:
                                order_form.add_error(None, 'Item does not exist in stock')
                                raise ValidationError('Item does not exist in stock')

                            # Check if enough stock is available
                            if item.get_current_qte < order.quantity:
                                order_form.add_error(None, f'Insufficient stock for {order.item.item_name}')
                                raise ValidationError(f'Insufficient stock for {order.item.item_name}')

                            # Update the stock
                            item.get_current_qte -= order.quantity
                            item.save()

                            order.sale = sale
                            order.save()

                    # Save Payment
                    payment = payment_form.save(commit=False)
                    payment.amount = sale.get_TTC
                    payment.save()

                    # Create SalePayment to link sale and payment
                    SalePayment.objects.create(sale=sale, payment=payment, amount_paid=payment.amount)

                # Redirect to sale detail view on success
                return redirect('sale:sale-detail', pk=sale.pk)

            except ValidationError as e:
                # Catch specific validation errors and display them
                print(f"Validation error: {e}")
            except Exception as e:
                # Catch general exceptions and log them
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
        item = Stock.objects.get(id=int(item_id))
        price = item.item.price
        description = item.item.description
        return JsonResponse({'price': price,'description':description}) 
    except Stock.DoesNotExist:
        return JsonResponse({'price': None})
    

def SaleDetailView(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale_payments = SalePayment.objects.filter(sale=sale)

    return render(request, 'sale/order_detail.html', {
        'sale': sale,
        'sale_payments': sale_payments,
    })

# # ////////////////// Ticket PDF ////////////////////////////////
def generate_sale_ticket(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale_payments = SalePayment.objects.filter(sale=sale)
    # Gather all the necessary data for the ticket
    context = {
        'company_info': {
            'name': 'Nina Bazar',
            'info': 'RC1021 ICE:001680586000002 PATENTE:49659021',
            'address': 'AV YOUSSEF BEN TACHFINE N138 GUELMIM',
            'phone': '06 72 38 17 47'
        },
        'sale': sale,
        'sale_payments': sale_payments,
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
# #/////////////////////////////// Devis /////////////////////////////////
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
class DealerCreate(View):
    template_name = 'sale/dealer_form.html'

    def get(self, request, *args, **kwargs):
        dealer_form = DealerForm()

        context = {
            'dealer_form': dealer_form,
        }
        return render(request, self.template_name, context)
    def post(self, request, *args, **kwargs):
        dealer_form = DealerForm(request.POST)
        if dealer_form.is_valid():
            dealer_form.save()

            return redirect('sale:dealer-list')
        context = {
            'dealer_form': dealer_form,
        }
        return render(request, self.template_name, context)
   

def safe_decimal_conversion(value):
        return Decimal(value or '0.00')


class SaleToDealerCreateView(View):
    template_name = 'sale/dealer_sale_form.html'

    def get(self, request, *args, **kwargs):
        sale_to_dealer_form = SaleToDealerForm()
        orders = OrderFormSet(queryset=Order_Line.objects.none())
        context = {
            'sale_to_dealer_form': sale_to_dealer_form,
            'orders': orders,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        sale_to_dealer_form = SaleToDealerForm(request.POST)
        orders = OrderFormSet(request.POST)

        if sale_to_dealer_form.is_valid() and orders.is_valid():
            try:
                with transaction.atomic():
                    sale = sale_to_dealer_form.save(commit=False)

                    # Calculate the total amount of the sale from the orders
                    total_sale_amount = 0
                    for order_form in orders:
                        if is_form_not_empty(order_form):
                            order = order_form.save(commit=False)
                            total_sale_amount += order.quantity * order.item.item.price  # Adjust based on your pricing logic

                    dealer = sale.dealer
                    total_sale = round(total_sale_amount * Decimal(1.20), 2)
                    # Check if dealer is active and if balance will exceed the limit
                    if dealer.is_active:
                        if dealer.balance + total_sale <= dealer.balance_limit:
                            # Save the sale since balance is within the limit
                            sale.save()

                            # Process Orders
                            for order_form in orders:
                                if is_form_not_empty(order_form):
                                    order = order_form.save(commit=False)

                                    # Fetch stock with row lock
                                    try:
                                        item = Stock.objects.get(item_id=order.item.item)
                                    except Stock.DoesNotExist:
                                        order_form.add_error(None, 'Item does not exist in stock')
                                        raise ValidationError('Item does not exist in stock')

                                    # Check stock availability
                                    if item.get_current_qte < order.quantity:
                                        order_form.add_error(None, f'Insufficient stock for {order.item.item_name}')
                                        raise ValidationError(f'Insufficient stock for {order.item.item_name}')

                                    # Update stock and save order
                                    item.get_current_qte -= order.quantity
                                    item.save()
                                    order.sale = sale
                                    order.save()

                            # Update dealer balance after processing all orders
                            dealer.balance += sale.get_TTC 
                            dealer.save()

                            return redirect('sale:sale-dealer-detail', pk=sale.pk)
                        else:
                            return redirect('sale:balance-limit-error')  # Balance limit exceeded
                    else:
                        return redirect('sale:dealer-blocked-error')  # Dealer inactive
                        
            except ValidationError as e:
                sale_to_dealer_form.add_error(None, str(e))
            except Exception as e:
                sale_to_dealer_form.add_error(None, f"Error saving sale: {e}")

        # Re-render form with errors
        context = {
            'sale_to_dealer_form': sale_to_dealer_form,
            'orders': orders,
        }
        return render(request, self.template_name, context)




def SaleToDealerDetails(request, pk):
    sale_to_dealer = get_object_or_404(SaleToDealer, pk=pk)
    return render(request, 'sale/dealer_order_detail.html', {'sale_to_dealer': sale_to_dealer})


class BalanceLimitErrorView(View):
    template_name = 'sale/balance_limit_error.html'

    def get(self, request, *args, **kwargs):
        context = {
            'error_message': "The dealer has exceeded the allowed balance limit and cannot proceed with the sale."
        }
        return render(request, self.template_name, context)

class DealerBlockedErrorView(View):
    template_name = 'sale/dealer_blocked_error.html'

    def get(self, request, *args, **kwargs):
        context = {
            'error_message': "The dealer is currently inactive and cannot proceed with the sale."
        }
        return render(request, self.template_name, context)


def SaleDealerList(request):
   dealers = Dealer.objects.all()
   return render(request, 'sale/dealer_list.html', {'dealers': dealers}) 


# #//////////////////////////////////// Facture ////////////////////////////////
def generate_facture_pdf(request, sale_id):
    sale_to_dealer = get_object_or_404(SaleToDealer, id=sale_id)
    context = {
        'sale_to_dealer': sale_to_dealer,
        'orders': sale_to_dealer.order_line_set.all(),
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
# #/////////////////////////////////// Bon Livraison ////////////////////////////////
def generate_bonLivraison_pdf(request, sale_id):
    sale_to_dealer = get_object_or_404(SaleToDealer, id=sale_id)
    context = {
        
        'sale_to_dealer': sale_to_dealer,
        'orders': sale_to_dealer.order_line_set.all(),
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
class MonthlyPaymentCreateView(View):
    template_name = 'sale/monthly_payment_form.html'

    def get(self, request):
        form = MonthlyPaymentForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = MonthlyPaymentForm(request.POST)
        if form.is_valid():
            dealer = form.cleaned_data['dealer']
            amount_paid = form.cleaned_data['amount']
           
            # Get all sales for this dealer
            sales = dealer.get_partial_and_unpaid_sales

            # Filter out unpaid and partially paid sales
            unpaid_sales = [
                sale for sale in sales
                if sum(payment.amount_paid for payment in sale.sale_payments.all()) < sale.get_TTC
            ]

            # Calculate total unpaid amount
            total_unpaid = sum(
                sale.get_TTC - sum(payment.amount_paid for payment in sale.sale_payments.all())
                for sale in unpaid_sales
            )

            # If amount_paid exceeds total unpaid, limit it to total unpaid
            amount_paid = min(amount_paid, total_unpaid)

            # Create the MonthlyPayment instance first
            monthly_payment = MonthlyPayment(dealer=dealer, amount=amount_paid)
            monthly_payment.save()  # Save it to the database first

            # Apply FIFO logic using transaction.atomic for safety
            with transaction.atomic():
                remaining_payment = amount_paid
                for sale in unpaid_sales:
                    sale_remaining = sale.get_TTC - sum(payment.amount_paid for payment in sale.sale_payments.all())

                    if remaining_payment <= 0:
                        break

                    if remaining_payment >= sale_remaining:
                        # Full payment for this sale
                        SalePayment.objects.create(
                            sale=sale,
                            payment=monthly_payment,
                            amount_paid=sale_remaining
                        )
                        remaining_payment -= sale_remaining
                    else:
                        # Partial payment for this sale
                        SalePayment.objects.create(
                            sale=sale,
                            payment=monthly_payment,
                            amount_paid=remaining_payment
                        )
                        remaining_payment = 0

           
            return redirect('sale:monthly-payment',pk=monthly_payment.pk)

        # If form is not valid, render the form with errors
        return render(request, self.template_name, {'form': form})



def MonthlyPaymentDetails(request, pk):
    payment = get_object_or_404(MonthlyPayment, pk=pk)
    dealer = payment.dealer
    total_unpaid_sales = dealer.total_unpaid
    context = {
        'dealer': dealer,
        'payment': payment,
    }

    return render(request, 'sale/monthly_payment_detail.html', context)
#///////////////////// Recu Payment ////////////////////////////////////
def generate_recu(request, payment_id):
    payment = get_object_or_404(MonthlyPayment, id=payment_id)
    dealer = payment.dealer
    amount = payment.amount
    date = payment.date

    context = {
        'company_info': {
            'name': 'Nina Bazar',
            'info': 'RC1021 ICE:001680586000002 PATENTE:49659021',
            'address': 'AV YOUSSEF BEN TACHFINE N138 GUELMIM',
            'phone': '06 72 38 17 47'
        },
        'dealer': dealer,
        'date':date,
        'amount':amount,
        'payment':payment,
    }
    # Render the reciep template with sale details
    html_string = render_to_string('sale/recu_payment.html', context)
    html = HTML(string=html_string,base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="P{payment.pk}.pdf"'
    return response                   

# #///////////////// return Sale /////////////////////////////////
class RefundCreateView(View):
    template_name = 'sale/refund_form.html'  

    def get(self, request, *args, **kwargs):       
        refund_form = RefundForm()
        orders = RefundFormSet()
        context = {
            'refund_form': refund_form,
            'orders': orders,
           
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        refund_form = RefundForm(request.POST)
        orders = RefundFormSet(request.POST)
        if refund_form.is_valid() and orders.is_valid():
            try:
                with transaction.atomic():
                    # Save the Sale
                    refund = refund_form.save(commit=False)
                    sale = Sale.objects.get(id=refund.so) #link to sale as foreign key
                    refund.sale = sale
                    refund.save()
                    
                    # Save Orders              
                    for order_form in orders:
                        if is_form_not_empty(order_form): 
                            order = order_form.save(commit=False)
                            try:
                                item = Stock.objects.get(id=order.item_id)
                            except Stock.DoesNotExist:
                                order_form.add_error(None, 'Item does not exist')
                                raise

                            item.get_current_qte += order.quantity
                            item.save()
                            order.refund= refund
                            order.save()
                    # Create in RefundPayment
                    RefundPayment.objects.create(
                            amount=refund.get_TTC,

                        )

            
                return redirect('sale:refund-detail', pk=refund.pk)  # Redirect to the sale detail view

            except Exception as e:
                # Log the exception for debugging if necessary
                print(f"Error saving sale: {e}")
                
        # If form is not valid or an exception occurs, re-render the form with errors
        context = {
            'refund_form': refund_form,
            'orders': orders,
        }
        return render(request, self.template_name, context)
    


def RefundDetails(request,pk):
    refund = get_object_or_404(Refund, pk=pk)
    sale = refund.sale
    context={
        'refund':refund,
        'sale': sale,
    }
    return render(request, 'sale/refund_detail.html',context)


# ///////////////////// Refund from  dealer ///////////////////

class RefundDealerCreateView(View):
    template_name = 'sale/refund_dealer_form.html'  

    def get(self, request, *args, **kwargs):       
        refund_form = RefundFromDealerForm()
        refunds = RefundFormSet()
        context = {
            'refund_form': refund_form,
            'refunds': refunds,
           
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        refund_form = RefundFromDealerForm(request.POST)
        refunds = RefundFormSet(request.POST)
        if refund_form.is_valid() and refunds.is_valid():
                with transaction.atomic():
                    # Save the refund
                    refund = refund_form.save(commit=False)
                    sale = Sale.objects.get(id=refund.so) #link to sale as foreign key
                    refund.sale = sale
                    refund.save()
                    
                    # Save refunds            
                    for refund_form in refunds:
                        if is_form_not_empty(refund_form): 
                            order = refund_form.save(commit=False)
                            try:
                                item = Stock.objects.get(id=order.item_id)
                            except Stock.DoesNotExist:
                                refund_form.add_error(None, 'Item does not exist')
                                raise

                            item.get_current_qte += order.quantity
                            item.save()
                            order.refund= refund
                            order.save()
                    # Create in RefundPayment
                    refund_payment =RefundPayment.objects.create(
                            amount=refund.get_TTC,
                        )
                    dealer = refund.dealer
                    refund_paid = refund.get_TTC
                    sales = dealer.get_partial_and_unpaid_sales

                    # Filter out unpaid and partially paid sales
                    unpaid_sales = [
                        sale for sale in sales
                        if sum(payment.amount_paid for payment in sale.sale_payments.all()) < sale.get_TTC
                    ]

                    # Calculate total unpaid amount
                    total_unpaid = sum(
                        sale.get_TTC - sum(payment.amount_paid for payment in sale.sale_payments.all())
                        for sale in unpaid_sales
                    )

                    # If amount_paid exceeds total unpaid, limit it to total unpaid
                    refund_paid = min(refund_paid, total_unpaid)


                    # Apply FIFO logic using transaction.atomic for safety
                    remaining_payment = refund_paid
                    for sale in unpaid_sales:
                        sale_remaining = sale.get_TTC - sum(payment.amount_paid for payment in sale.sale_payments.all())

                        if remaining_payment <= 0:
                            break

                        if remaining_payment >= sale_remaining:
                        # Full payment for this sale
                            SalePayment.objects.create(
                                sale=sale,
                                payment=refund_payment,
                                amount_paid=sale_remaining
                            )
                            remaining_payment -= sale_remaining
                        else:
                            # Partial payment for this sale
                            SalePayment.objects.create(
                                sale=sale,
                                payment=refund_payment,
                                amount_paid=remaining_payment
                                )
                            remaining_payment = 0
                    #upda te balance of dealer 
                    dealer.balance -= refund_paid
                    dealer.save()        

                
                return redirect('sale:refund-dealer-payment',pk=refund.pk)

        context = {
            'refund_form': refund_form,
            'refunds': refunds,
           
        }        # If form is not valid, render the form with errors
        return render(request, self.template_name, context)


            
def RefundDealerDetails(request,pk):
    refund = get_object_or_404(Refund, pk=pk)
    sale = refund.sale
    context={
        'refund':refund,
        'sale': sale,
    }
    return render(request, 'sale/refund_detail.html',context)            

#////////////////////// generate refund from dealer //////////////
def generate_refund(request, refund_id):
    refund = get_object_or_404(RefundFromDealer, id=refund_id)
    dealer = refund.dealer
    amount = refund.get_TTC
    date = refund.date

    context = {
        'company_info': {
            'name': 'Nina Bazar',
            'info': 'RC1021 ICE:001680586000002 PATENTE:49659021',
            'address': 'AV YOUSSEF BEN TACHFINE N138 GUELMIM',
            'phone': '06 72 38 17 47'
        },
        'dealer': dealer,
        'date':date,
        'amount':amount,
        'refund':refund,
    }
    # Render the reciep template with sale details
    html_string = render_to_string('sale/refund_bill.html', context)
    html = HTML(string=html_string,base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="R{refund.pk}.pdf"'
    return response     