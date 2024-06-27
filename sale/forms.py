from django import forms
from django.forms import inlineformset_factory
from sale.models import (Sale,
                          Order)



class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer']



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['item','quantity']
        # exclude = ['description','price','subtotal']

OrderFormSet = inlineformset_factory(Sale,Order,form=OrderForm,
                extra=1,can_delete=True,can_delete_extra=True)        