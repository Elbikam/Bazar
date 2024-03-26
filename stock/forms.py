
from django import forms



class TheForm(forms.Form):
    type_the = [("chaara","Chaara"), ("mkarkab","Mkarkab"),]
    embalage_the =[("carton","carton"),("zanbile","zanbile"),("cadeau","cadeau"),("sac","sac"), ("Khshab","khshab"),]
    poid_choice=[('200','200'),('500','500'),('1000','1000'),('2000','2000'),('3000','3000'),]
    ref_choice=[('9366','9366'),('9371','9371'),('9375','9375'),('4011','4011'),('41022','41022'),('3505B','3505B'),]
    code = forms.CharField(max_length=13)
    date = forms.DateTimeField()
    qte = forms.IntegerField(min_value=1)
    price = forms.DecimalField(label="prix")
    brand = forms.CharField(max_length=30)
    type = forms.ChoiceField(label="type of The'", choices=type_the)
    poid = forms.ChoiceField(label="poid (g)", choices=poid_choice)
    ref = forms.ChoiceField(label="referance", choices=ref_choice)
    embalage= forms.ChoiceField(choices=embalage_the)
