from django.shortcuts import render
from django.http import HttpRequest
from .forms import TheForm
from stock.models import The
from stock.forms import TheForm

# Create your views here.
def index(request):
    return render(request,"stock/index.html",{'index':'Nina Bazar'})

#----------------------------------------------------------------------
def add_item(request):
    if request.method == 'POST':
        form = TheForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            date = form.cleaned_data['date']
            qte = form.cleaned_data['qte']
            price = form.cleaned_data['price']
            brand = form.cleaned_data['brand']
            type = form.cleaned_data['type']
            poid = form.cleaned_data['poid']
            ref = form.cleaned_data['ref']
            embalage = form.cleaned_data['embalage']

            # Retrieve item from database using barcode
            try:
                item = The.objects.get(code=code)
                message = f">>> item with barcode {code} already exists."
            except The.DoesNotExist:
                item = The.objects.create(code=code,date=date,qte=qte,price=price,brand=brand,type=type,poid=poid,ref=ref,embalage=embalage)
                message = f"Item '{brand}' with barcode {code} has been added."
                
            return render(request, 'stock/add_item.html', {'form': form, 'message': message})
    else:
        form = TheForm()
    return render(request, 'stock/add_item.html', {'form': form})

 #---------------------------------------------------------------------------------
def list(request):
    l=The.objects.all()
    return render(request,'stock/list.html',{'list':l})