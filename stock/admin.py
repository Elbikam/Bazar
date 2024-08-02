from django.contrib import admin

# Register your models here.
# stock/admin.py

# stock/admin.py


from .models import Item, The,Parfum

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'description', 'price')
    search_fields = ('item', 'description')

class TheItemAdmin(ItemAdmin):  # Inherit from ItemAdmin
    list_display = ('id', 'item', 'description', 'price', 'category','packaging','ref',
                    'weight')
    search_fields = ('id','date','item','description','price','category','weight','packaging','ref')  # Additional search field


class ParfumItemAdmin(ItemAdmin):  # Inherit from ItemAdmin
    list_display = ('id', 'item', 'description', 'price', 'sub_brand')
    search_fields = ('item', 'description', 'volum','type')  # Additional search field
admin.site.register(Item, ItemAdmin)
admin.site.register(The, TheItemAdmin)
admin.site.register(Parfum, ParfumItemAdmin)

