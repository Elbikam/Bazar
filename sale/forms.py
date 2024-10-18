from django import forms
from sale.models import *
from django.forms import inlineformset_factory,ModelForm
from stock.models import Item
from django.utils import timezone
# /////////////////////// sale Form ////////////////////////////////
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [] 
        exclude = ['date']  

class OrderLineForm(forms.ModelForm):
    class Meta:
        model = Order_Line
        fields = ['item','description','quantity','price']
        widgets = {
            'item': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Edite price'}),}

OrderFormSet = inlineformset_factory(
    Sale, Order_Line, form=OrderLineForm,
    extra=1, can_delete=True,
    error_messages={'item': {'required': 'Please enter a correct ID'}}
)  

# #////////////////////////// Devis Form ///////////////////////////////////    
class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['customer']
       

class DevisLineForm(forms.ModelForm):
    class Meta:
        model = Devis_Line
        fields = ['item','description','quantity','price']
        widgets = {
            'item': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Edite price'}),}

DOrderFormSet = inlineformset_factory(
    Devis, Devis_Line, form=DevisLineForm,
    extra=1, can_delete=True,
    error_messages={'item': {'required': 'Please enter a correct ID'}})

# # //////////////////////////  Payment Form ////////////////////////////// 
class CashPaymentForm(forms.ModelForm):
    class Meta:
        model = CashPayment
        fields = ['cash_received']


# #///////////////////////////  Dealer Form /////////////////////////////////
class DealerForm(forms.ModelForm):
    class Meta:
        model = Dealer
        fields = ['name','phone_whatsapp','balance_limit']
        
        
# #/////////////////////////// Dealer Sale Form /////////////////////////////
class SaleToDealerForm(forms.ModelForm):
    class Meta:
        model = SaleToDealer
        fields = ['dealer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the widget
        self.fields['dealer'].widget.attrs.update({'dealer': 'custom-select'})    

# #//////////////////////////// Monhtly Payment Form ///////////////////////

class MonthlyPaymentForm(forms.ModelForm):
    class Meta:
        model = MonthlyPayment
        fields = ['dealer', 'amount']  # You can include other fields if necessary
        widgets = {
            'dealer': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("The amount must be greater than zero.")
        return amount

# #//////////////////////////////////////////// Refund Sale //////////////////////////////////////////////////
class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['so','reason'] 
      
class RefundFromDealerForm(forms.ModelForm):
    class Meta:
        model = RefundFromDealer
        fields = ['so','dealer','reason']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['dealer'].widget.attrs.update({'dealer': 'custom-select'})   

class RefundLineForm(forms.ModelForm):
    class Meta:
        model = Refund_Line
        fields = ['item','description','quantity','price']
        widgets = {
            'item': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Edite price'}),}

RefundFormSet = inlineformset_factory(
    Refund, Refund_Line, form=RefundLineForm,
    extra=1, can_delete=True,
    error_messages={'item': {'required': 'Please enter a correct ID'}}
)  
