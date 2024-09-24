from django import forms
from stock.models import The, Parfum,Item
from django.forms import inlineformset_factory,ModelForm
from django.contrib.contenttypes.models import ContentType

# //////////////////// Item form  //////////////////////////
class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['id','item','description','qte_by_carton','quantity','alert_qte','price']

class ItemSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)

# ///////////////////// The form ///////////////////////////////

class TheForm(forms.ModelForm):
    SUBCAT_CHOICES = [
    ('CHAARA', 'CHAARA'),
    ('MKARKAB', 'MKARKAB'),
    ]
    PACKAGE_CHOICES = [
    ('CARTON', 'CARTON'),
    ('ZANBIL', 'ZANBIL'),
    ('CADEAU', 'CADEAU'),
     ('KHSHAB', 'KHSHAB'),
    ]
    WEIGHT_CHOICES = [
    ('100', '100'),    
    ('200', '200'),
    ('500', '500'),
    ('1000', '1000'),
    ('2000', '2000'),
    ('3000', '3000'),
    ]
    REFERANCE_CHOICES = [
    ('9366', '9366'),
    ('9371', '9371'),
    ('9375', '9375'),
    ('4011', '4011'),
    ('41022', '41022'),
    ('3505B', '3505B'),
    ('41022', '41022'),
    ]
    id = forms.IntegerField()
    item  = forms.CharField()
    description = forms.CharField(max_length=50)
    quantity = forms.IntegerField()
    alert_qte = forms.IntegerField()
    price = forms.DecimalField(max_digits=5, decimal_places=2)
    category = forms.ChoiceField(choices=SUBCAT_CHOICES)
    packaging = forms.ChoiceField(choices=PACKAGE_CHOICES)
    weight = forms.ChoiceField(choices=WEIGHT_CHOICES)
    ref = forms.ChoiceField(choices=REFERANCE_CHOICES)
    
    class Meta:
        model = The
        fields = ['id','item','description','qte_by_carton','quantity','alert_qte','price','category','packaging','weight','ref']
        

#///////////////////////////////  Perfum //////////////////////////////////////////
class ParfumForm(forms.ModelForm):
    TYPE_CHOICES = [
    ('MAN', 'MAN'),
    ('WOMEN', 'WOMEN'),
    ('ALL', 'ALL'),
    ]

    VOLUM_CHOICES = [
    ('100 ml', '100 ml'),
    ('500 ml', '500 ml'),
    ('1000 ml', '1000 ml'),
    ]
    alert_qte = forms.IntegerField()
    sub_brand = forms.CharField(max_length=30)
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    volum = forms.ChoiceField(choices=VOLUM_CHOICES)
    class Meta:
        model = Parfum
        fields = ['id','item','description','qte_by_carton','quantity','alert_qte','price','sub_brand','type','volum']
 
        

# /////////////////////////// Item Search ////////////////////////////////////
class ItemSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)