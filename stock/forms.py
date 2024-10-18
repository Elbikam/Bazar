from django import forms
from .models import Item,ReceiptItem,StockAlert,Receipt
from django.views.generic import ListView
from django.forms import modelformset_factory
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['id','name', 'category', 'description','price'] 


class ItemListView(ListView):
    model = Item
    template_name = 'item_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(name__icontains=query)  # Search by item name
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ItemSearchForm(self.request.GET)  
        return context


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['bon_de_livrason','qte_total','qte_by_carton'] 
    
    


class ReceiptItemForm(forms.ModelForm):
    class Meta:
        model = ReceiptItem
        fields = ['item', 'description','quantity', 'unit_by_carton']

    item = forms.CharField(label="Item ID", widget=forms.TextInput(attrs={'placeholder': 'Enter Item ID'}))
    def clean_item(self):
        item_id = self.cleaned_data['item']
        try:
            return Item.objects.get(id=item_id)  # Fetch the Item instance based on the ID
        except Item.DoesNotExist:
            raise ValidationError("Invalid item ID. Please enter a valid ID.")


ReceiptItemFormSet = inlineformset_factory(
    Receipt, ReceiptItem, form=ReceiptItemForm, extra=1,can_delete=True, 
   )



class ItemSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100, required=False)
    category = forms.ChoiceField(choices=[('', 'All')] + Item.CAT_CHOICES, required=False)



class StockAlertForm(forms.ModelForm):
    class Meta:
        model = StockAlert
        fields = ['item', 'threshold']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, customize widget or help_text
        self.fields['threshold'].help_text = 'Set the minimum stock level for alerts.'

