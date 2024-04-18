from django import forms
from .models import *

class ClientForm(forms.Form):
    client = forms.CharField()
class OrderForm(forms.Form):
    client = forms.CharField()

class OrderDetailsForm(forms.Form):
    sale_id = forms.NumberInput()
    item = forms.CharField()
    qte = forms.IntegerField(min_value=1)











