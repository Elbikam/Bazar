from .models import *
from django.utils import timezone
def operations(request):
    context = {}

    # Get today's sales and total sales
    today = timezone.now().date()
    sales_today = Sale.objects.filter(date__date=today)
    #Sales to Distributors
    sales_to_distributor = SaleToDealer.objects.filter(date__date=today)
    total_sales_to_distributor = sum(sale.get_TTC for sale in sales_to_distributor) if sales_to_distributor else 0
    #Sales to Individuals
    sales_to_individual = SaleToPersone.objects.filter(date__date=today)
    total_sales_to_individuals = sum(sale.get_TTC for sale in sales_to_individual) if sales_to_individual else 0
    orders=sum(sale.order_line_set.count() for sale in sales_today) if sales_today else 0
    transaction_today = Sale.objects.filter(date__date=today)
    transactions = transaction_today.count()
    


    # Get today's refunds, cash payments, and monthly payments
    total_refunds_today = RefundPayment.objects.filter(date__date=today).aggregate(total=Sum('amount'))['total'] or 0
    total_cash_payments_today = CashPayment.objects.filter(date__date=today).aggregate(total=Sum('amount'))['total'] or 0
    total_monthly_payments_today = MonthlyPayment.objects.filter(date__date=today).aggregate(total=Sum('amount'))['total'] or 0
        
        # Add context data
    context['total_sales_to_individuals'] =  total_sales_to_individuals
    context['total_sales_to_distributor'] = total_sales_to_distributor
    context['total_refunds_today'] = total_refunds_today
    context['total_cash_payments_today'] = total_cash_payments_today
    context['total_monthly_payments_today'] = total_monthly_payments_today
    context['transaction'] = transactions
    return context
