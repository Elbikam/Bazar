
from django.contrib import admin
from .models import *

class ReceiptItemInline(admin.TabularInline):  # Correctly inheriting from admin.TabularInline
    model = ReceiptItem
    extra = 1  # Number of empty forms to show in the inline section



@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('item', 'current_quantity', 'unit_by_carton', 'quantity_by_crtn')
    readonly_fields = ('quantity_by_crtn',)
    search_fields = ('item__name',)
    actions = ['check_stock_alert']

    def check_stock_alert(self, request, queryset):
        for stock in queryset:
            stock.check_stock_alert()
        self.message_user(request, "Stock alerts checked for selected items.")
    check_stock_alert.short_description = "Check stock alerts for selected items"

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id','date', 'bon_de_livraison', 'get_qte_total', 'get_qte_carton')
    search_fields = ('id',)
    inlines = [ReceiptItemInline]  # Including the ReceiptItem inline

@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ('receipt', 'item', 'quantity', 'qte_by_carton')
    search_fields = ('item__name', 'receipt__bon_de_livraison')

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('item', 'threshold', 'created_at')
    search_fields = ('item__item__name',)
    list_filter = ('created_at',)

@admin.register(The)
class TheAdmin(admin.ModelAdmin):
    list_display = ('id','name','description','cost_price','price','ref','category','weight')
    search_fields = ('id',)
    list_filter = ('ref','weight')