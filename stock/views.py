from django.shortcuts import render, redirect
from django.http import HttpRequest

from stock.models import *
from stock.forms import *
from datetime import date
from django.core import validators
#-----------------------------------------------------------------------
# Create your views here.
def index(request):
    return render(request,"stock/index.html",{'index':'Nina Bazar'})

#----------------------------------------------------------------------
def add_The(request):
    if request.method == 'POST':
        form = TheForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            brand = form.cleaned_data['brand']
            qte_entry = form.cleaned_data['qte_entry']
            qte_onHand = form.cleaned_data['qte_onHand']
            price = form.cleaned_data['price']
            type = form.cleaned_data['type']
            poid = form.cleaned_data['poid']
            ref = form.cleaned_data['ref']
            embalage = form.cleaned_data['embalage']
            try:
                item = The.objects.get(id=id)
                message = f">>> item with barcode {id} already exists."
            except The.DoesNotExist:
                item = The.objects.create(id=id,brand=brand,qte_entry=qte_entry,qte_onHand =qte_onHand,price=price,type=type,poid=poid,ref=ref,embalage=embalage)
                message = f"Item '{brand}' with barcode {id} has been added."
                
            return render(request,'stock/add_The.html', {'form': form,'message':message})
    else:
        form = TheForm()
    return render(request, 'stock/add_The.html', {'form': form})

#/////////////////////////////////////////////////////////////////////////////////////////////////
def list(request):
    l=The.objects.all()
    return render(request,'stock/list.html',{'list':l})
#//////////////////////////////////////////////////////////////////////////////////////////////////

def search_view(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        results = []
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
            results = Barcode.objects.filter(brand__icontains=search_query)
        return render(request, 'stock/search.html', {'form': form, 'results': results})

#///////////////////////////////////////////////////////////////////////////////////////////////////// 

def add_Parfum(request):
    if request.method == 'POST':
        form = ParfumForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            qte_entry = form.cleaned_data['qte_entry']
            qte_onHand = form.cleaned_data['qte_onHand']
            price = form.cleaned_data['price']
            brand = form.cleaned_data['brand']
            sub_brand = form.cleaned_data['sub_brand']
            type_parf = form.cleaned_data['type_parf']
            volume = form.cleaned_data['volume']
          
            try:
                item = Parfum.objects.get(id=id)
                message = f">>> item with barcode {id} already exists."
            except Parfum.DoesNotExist:
                item = Parfum.objects.create(id=id,qte_entry=qte_entry,qte_onHand=qte_onHand,price=price,brand=brand,sub_brand=sub_brand,volume=volume)
                message = f"Item '{brand}' and with barcode {id} has been added."
                
            return render(request,'stock/add_Parfum.html', {'form': form,'message':message})
    else:
        form = ParfumForm()
    return render(request, 'stock/add_Parfum.html', {'form': form})
    f
