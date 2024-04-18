from django.shortcuts import render, redirect
from vente.models import *
from vente.forms import *

# Create your views here.
def index(request):
    return render(request,"vente/index_vente.html",{'index':'Nina Bazar'})

def add_order(request):
    if request.method == 'POST':
        form = OrderDetailsForm(request.POST)
        if form.is_valid():
            c = Customer.objects.create()
            sale_id = form.cleaned_data['sale_id']
            item = form.cleaned_data['item']
            qte = form.cleaned_data['qte']
            itm = Barcode.objects.get(pk=item)
            description = itm.brand
            price = itm.price



            od = CreateOrder.objects.create(sale_id = sale_id, item=itm, description=description, qte=qte,price = price)

        return render(request, 'vente/add_order.html',{'form':form})
    else:
        form = OrderDetailsForm()  
        return render(request,'vente/add_order.html', {'form':form})


