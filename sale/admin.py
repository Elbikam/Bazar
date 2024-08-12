from django.contrib import admin

from sale.models import Sale, Order,Persone,Customer

class PersoneAdmin(admin.ModelAdmin): 
    list_display = ['customer']
   
    
    
class OrderInline(admin.TabularInline):  # or admin.StackedInline
    model = Order
    extra = 1  # Number of extra forms to display  
class SaleAdmin(admin.ModelAdmin):

    list_display = ('sale_id', 'customer', 'date', 'get_HT', 'get_TVA', 'get_TTC')
    search_fields = ('sale_id', 'customer')
    list_filter = ('date',)
    inlines = [OrderInline]
 

admin.site.register(Sale, SaleAdmin)
admin.site.register(Order)
admin.site.register(Persone,PersoneAdmin)