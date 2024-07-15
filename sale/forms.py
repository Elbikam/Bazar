from django import *
from django.forms import inlineformset_factory,ModelForm
from sale.models import (Sale,
                          Order)



class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ['phone']
        exclude = ()
        
        



class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['item','quantity']
        
        # exclude = ['description','price','subtotal']

OrderFormSet = inlineformset_factory(Sale,Order,form=OrderForm,
                extra=1,can_delete=True,can_delete_extra=True,error_messages='plz entre correct word')        