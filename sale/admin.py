from django.contrib import admin
from .models import Sale, Refund, Devis, Order_Line, Devis_Line, Refund_Line, Dealer, SaleToDealer, RefundFromDealer, CashPayment, MonthlyPayment, SalePayment

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'get_TTC', 'total_of_items')
    search_fields = ('id',)

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'so', 'sale', 'reason', 'get_TTC', 'total_of_items')
    search_fields = ('so',)

@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'get_HT', 'total_of_items')
    search_fields = ('customer',)

@admin.register(Order_Line)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'item', 'quantity', 'price', 'get_subtotal')
    search_fields = ('sale__id',)

@admin.register(Devis_Line)
class DevisLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'devis', 'item', 'quantity', 'price', 'get_subtotal')
    search_fields = ('devis__id',)

@admin.register(Refund_Line)
class RefundLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'refund', 'item', 'quantity', 'price', 'get_subtotal')
    search_fields = ('refund__id',)

@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_whatsapp', 'is_active', 'balance')
    search_fields = ('name', 'phone_whatsapp')

@admin.register(SaleToDealer)
class SaleToDealerAdmin(admin.ModelAdmin):
    list_display = ('id', 'dealer', 'date', 'get_TTC', 'amount_due')
    search_fields = ('id',)

@admin.register(RefundFromDealer)
class RefundFromDealerAdmin(admin.ModelAdmin):
    list_display = ('id', 'dealer', 'sale', 'get_HT')
    search_fields = ('dealer__name',)

@admin.register(CashPayment)
class CashPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'cash_received', 'get_change')
    search_fields = ('payment__id',)

@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'dealer', 'amount', 'date')
    search_fields = ('dealer__name',)



