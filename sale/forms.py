from django import forms
from sale.models import Sale,InlineOrder,InlineDevis,Payment,Vendor,Sale_Vendor,Cash,Devis
from django.forms import inlineformset_factory,ModelForm
from stock.models import Item

# /////////////////////// sale Form ////////////////////////////////
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale 
        exclude = ['date']  

class InlineOrderForm(forms.ModelForm):
    class Meta:
        model = InlineOrder
        fields = ['item','quantity','price','refunded']
        widgets = {
            'item': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Edite price'}),}

OrderFormSet = inlineformset_factory(
    Sale, InlineOrder, form=InlineOrderForm,
    extra=1, can_delete=True,
    error_messages={'item': {'required': 'Please enter a correct ID'}}
)  

#////////////////////////// Devis Form ///////////////////////////////////    
class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['customer']
       

class InlineDevisForm(forms.ModelForm):
    class Meta:
        model = InlineDevis
        fields = ['item','quantity','price']
        widgets = {
            'item': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Edite price'}),}

DOrderFormSet = inlineformset_factory(
    Devis, InlineDevis, form=InlineDevisForm,
    extra=1, can_delete=True,
    error_messages={'item': {'required': 'Please enter a correct ID'}})

# //////////////////////////  Payment Form //////////////////////////////          
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['sale'] 
class CashForm(forms.ModelForm):
    class Meta:
        model = Cash
        fields = ['amount_received', 'is_pay']
        exclud= ['sale']


#///////////////////////////  Vendor Form /////////////////////////////////
class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name','city','phone_whatsapp']
        
#/////////////////////////// Vendor Sale Form /////////////////////////////
class VendorSaleForm(forms.ModelForm):
    class Meta:
        model = Sale_Vendor
        fields = ['vendor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the widget
        self.fields['vendor'].widget.attrs.update({'vendor': 'custom-select'})    