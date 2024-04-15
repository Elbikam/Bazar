
from django import forms
from datetime import datetime


class TheForm(forms.Form):
    #super class
    type_the = [("chaara","Chaara"), ("mkarkab","Mkarkab"),]
    embalage_the =[("carton","carton"),("zanbile","zanbile"),("cadeau","cadeau"),("sac","sac"), ("Khshab","khshab"),]
    poid_choice=[('200','200'),('500','500'),('1000','1000'),('2000','2000'),('3000','3000'),]
    ref_choice=[('9366','9366'),('9371','9371'),('9375','9375'),('4011','4011'),('41022','41022'),('3505B','3505B'),]
    id = forms.CharField(min_length=8,max_length=13)
    brand = forms.CharField(max_length=30,label="brand")
    qte_entry = forms.IntegerField(min_value=1,label="qte_entry")
    qte_onHand = forms.IntegerField(min_value=1,label="qte_onHand")
    price = forms.DecimalField(label="prix")
    type = forms.ChoiceField(label="type", choices=type_the)
    poid = forms.ChoiceField(label="poid (g)", choices=poid_choice)
    ref = forms.ChoiceField(label="ref", choices=ref_choice)
    embalage= forms.ChoiceField(choices=embalage_the,label="embalage")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class SearchForm(forms.Form):
    search_query = forms.CharField(label='Search')
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////    

class ParfumForm(forms.Form):
    type_p = [('M','Man'),('W','Woman'),('A','All')]
    id = forms.CharField(max_length=13,)
    brand = forms.CharField(max_length=30,label="brand")
    qte_entry = forms.IntegerField(min_value=1,label="qte_entry")
    qte_onHand = forms.IntegerField(min_value=1,label="qte_onHand")
    price = forms.DecimalField(label="prix")
    sub_brand = forms.CharField(max_length=30,label="sub_brand parfum")
    type_parf = forms.ChoiceField(choices=type_p,label="type parfum")
    volume = forms.CharField(max_length=10,label="volume (ml)")


