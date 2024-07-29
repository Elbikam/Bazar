from django import *
from django.forms import inlineformset_factory,ModelForm
from sale.models import (Sale,
                          Order,Ticket)


from django import forms
class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ['customer']
        exclude = ()
        
        



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['item_id', 'quantity']
        widgets = {
            'item_id': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
        }

    price = forms.DecimalField(max_digits=6, decimal_places=2, required=False, widget=forms.HiddenInput())

OrderFormSet = inlineformset_factory(Sale,Order,form=OrderForm,
                extra=1,can_delete=True,can_delete_extra=True,error_messages='plz entre correct word')        




class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['customer_name', 'issue_description']
