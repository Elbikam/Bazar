from django.contrib import admin

from sale.models import Sale, InlineOrder,Sale_Vendor,Vendor
 
    
class OrderInline(admin.TabularInline):  # or admin.StackedInline
    model = InlineOrder
    extra = 1  # Number of extra forms to display  
class SaleAdmin(admin.ModelAdmin):
    list_display = ( 'date', 'get_HT', 'get_TVA', 'get_TTC','total_of_items')
    search_fields = ('id',)
    list_filter = ('date',)
    inlines = [OrderInline]
 
class SaleVendorAdmin(admin.ModelAdmin):
    list_display = ( 'date', 'get_HT', 'get_TVA', 'get_TTC','total_of_items')
    search_fields = ('id',)
    list_filter = ('date',)
    inlines = [OrderInline]



class VendorAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'city', 'phone_whatsapp',
                     'total_amount_received','total_sales',
                     'count_sales','balance')
    search_fields = ('name',)
    





admin.site.register(Sale, SaleAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Sale_Vendor, SaleAdmin)
admin.site.register(InlineOrder)
