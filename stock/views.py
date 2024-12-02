from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from decimal import Decimal, InvalidOperation,getcontext
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import *
from .forms import TheForm, ReceiptItemForm,ItemSearchForm,StockAlertForm,ReceiptItemFormSet,ReceiptForm,StockSearchForm
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages  # For displaying messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
#////////////////////////////// Function check is empty form ///////////////////////////////////////
def is_form_not_empty(form):
    return any(field.value() for field in form if field.name != 'DELETE')

def is_formset_not_empty(formset):
    return any(is_form_not_empty(form) for form in formset)

# //////////////////////////////////////////////////////
class TheCreateView(CreateView):
    model = The
    form_class = TheForm
    template_name = 'stock/the_form.html'
    success_url = reverse_lazy('stock:item_list')  # Update with your item list URL name

class TheListView(ListView):
    model = The
    template_name = 'stock/the_list.html'
    context_object_name = 'The'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')
        category = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )

        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ItemSearchForm(self.request.GET)  
        return context
    
class ReceiptCreateView(LoginRequiredMixin,View):
    login_url = 'dashboard:login' 
    template_name = 'stock/receipt_form.html'

    def get(self, request, *args, **kwargs):
        receipt_form = ReceiptForm()
        items = ReceiptItemFormSet()
        return render(request, self.template_name, {
            'receipt_form': receipt_form,
            'items': items,
        })

    def post(self, request, *args, **kwargs):
        receipt_form = ReceiptForm(request.POST)
        items = ReceiptItemFormSet(request.POST)

        if receipt_form.is_valid() and items.is_valid():
            with transaction.atomic():
                receipt = receipt_form.save(commit=False)
                receipt.user = request.user
                receipt.save()

                for receipt_item_form in items:
                    if is_form_not_empty(receipt_item_form):
                        receipt_item = receipt_item_form.save(commit=False)
                        item_id = receipt_item.item
                        try:
                            receipt_item.item = item_id
                        except Item.DoesNotExist:
                            receipt_item.item = None  # Or handle the error as needed
                        receipt_item.receipt = receipt  # link foreign key
                        receipt_item.save()

          
            return redirect('stock:receipt-detail', pk=receipt.pk)

        else:
            messages.error(request, 'There was an error with your form. Please check and try again.')

            context = {
                'receipt_form': receipt_form,
                'items': items,
            }
            return render(request, self.template_name, context)


class ReceiptDetailView(DetailView):
    model = Receipt
    template_name = 'stock/receipt_detail.html'  # Template for the receipt detail
    context_object_name = 'receipt'  # Context variable for the single receipt

def stock_alert_view(request):
    alerts = StockAlert.objects.all()
    return render(request, 'stock/stock_alerts.html', {'alerts': alerts})


class StockAlertCreateView(View):
    template_name = 'stock/stock_alert_form.html'

    def get(self, request):
        form = StockAlertForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = StockAlertForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Stock alert created successfully!')
            return redirect('stock:alert_success')  # Redirect to a success page
        else:
            # messages.error(request, 'There were errors in the form. Please correct them.')  # Error message
            return render(request, self.template_name, {'form': form})
    
class AlertSuccessView(View):
    def get(self, request):
        return render(request, 'stock/alert_success.html')  # Create this template  



def filter_items(request):
    category = request.GET.get('category', None)
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)

    items = Item.objects.all()

    # Apply filters based on the request parameters
    if category:
        items = items.filter(category=category)
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    # Return the filtered items in JSON format
    item_list = [{'id': item.id, 'name': item.name, 'description': item.description} for item in items]
    return JsonResponse({'items': item_list})



def fetch_items(request):
    item_id = request.GET.get('item_id')
    try:
        item = Item.objects.get(id=item_id)
        response_data = {
            'id': item.id,
            'description': item.description,
        }
        return JsonResponse(response_data)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found.'}, status=404)

class ReceiptListView(ListView):
    model = Receipt
    template_name = 'stock/receipt_list.html'  # Template for the receipt list
    context_object_name = 'receipts'  # Context variable for the list of receipts

    def get_queryset(self):
        # Optional: Add any filtering or ordering logic here
        return super().get_queryset().order_by('-date')  # Order by date descending
    



def search_item_in_stock(request):
    """View to handle searching items in stock."""
    form = StockSearchForm()
    results = Stock.objects.all()  # Start with all Stock items

    if request.method == 'GET':
        query = request.GET.get('query')

        if query:
            results = results.filter(item__name__icontains=query) | results.filter(item__description__icontains=query)



    return render(request, 'stock/stock_search.html', {'form': form, 'results': results})
