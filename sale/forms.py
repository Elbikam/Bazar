from django import forms
from sale.models import Payment,Vendor,Devis,Sale,Order_Line,Devis_Line,SaleToVendor,ReturnSale,Return_Line
from django.forms import inlineformset_factory,ModelForm
from stock.models import Item
from django.utils import timezone
# /////////////////////// sale Form ////////////////////////////////
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        exclude = ['date','is_returned']  

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

#////////////////////////// Devis Form ///////////////////////////////////    
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

# //////////////////////////  Payment Form //////////////////////////////          
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_received', 'is_pay']
      

#///////////////////////////  Vendor Form /////////////////////////////////
class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name','city','phone_whatsapp']
        
        
#/////////////////////////// Vendor Sale Form /////////////////////////////
class SaleToVendorForm(forms.ModelForm):
    class Meta:
        model = SaleToVendor
        fields = ['vendor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the widget
        self.fields['vendor'].widget.attrs.update({'vendor': 'custom-select'})    

#//////////////////////////// Monhtly Payment Form ///////////////////////

class MonthlyPaymentForm(forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), label="Select Vendor")
    class Meta:
        model = Payment
        fields = ['vendor', 'amount_received']

#//////////////////////////////////////////// Return Sale //////////////////////////////////////////////////
class ReturnSaleForm(forms.ModelForm):
    class Meta:
        model = ReturnSale
        fields = ['so'] 

class ReturnSaleLineForm(forms.ModelForm):
    class Meta:
        model = Return_Line
        fields = ['item','description','quantity','price']
        widgets = {
            'item': forms.TextInput(attrs={'placeholder': 'Enter item ID'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Edite price'}),}

ReturnFormSet = inlineformset_factory(
    ReturnSale, Return_Line, form=ReturnSaleLineForm,
    extra=1, can_delete=True,
    error_messages={'item': {'required': 'Please enter a correct ID'}}
)  