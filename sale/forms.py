from django import *
from django.forms import inlineformset_factory,ModelForm
from sale.models import (Sale,
                          Order,Persone,Customer,Revendeur,Payment,Cash,Ticket)

from django.contrib.contenttypes.models import ContentType
from django import forms


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        exclude = ['sale_id','customer']  # Exclude sale_id if it's causing issues

    def __init__(self, *args, **kwargs):
        persone = kwargs.pop('persone', None)
        super(SaleForm, self).__init__(*args, **kwargs)
        if persone:
            self.instance.customer = persone  # Set the customer from persone_form

    
class PersoneForm(forms.ModelForm):
    class Meta:
        model = Persone
        fields = ['customer'] 
 
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['item_id','quantity','price']
        widgets = {
            'item_id': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Edite price'}),
        }

    # price = forms.DecimalField(max_digits=6, decimal_places=2, required=False, widget=forms.HiddenInput())
   

OrderFormSet = inlineformset_factory(Sale,Order,form=OrderForm,
                extra=1,can_delete=True,can_delete_extra=True,error_messages='plz entre correct item ID')        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['sale_id'] 
class CashForm(forms.ModelForm):
    class Meta:
        model = Cash
        fields = ['amount_received', 'is_pay']
        exclud= ['sale_id']

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['customer_name', 'issue_description']
