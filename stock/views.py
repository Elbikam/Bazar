from django.db.models.base import Model as Model
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from .models import The, Item, Parfum
from django.views.generic import ( 
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView    
    )
from .forms import TheForm, ParfumForm,ItemSearchForm
from sale.models import Sale,Order
from collections import defaultdict
from django.db.models import Q

def dashboard():
    pass
class ItemListView(ListView):
    model = Item
    queryset = Item.objects.all()
    
class  ItemDetailView(DetailView):
    model = Item

    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Item, id=id_)
    

class ItemDeleteView(DeleteView):
    model = Item 
    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Item, id=id_)
    def get_success_url(self):
        return reverse('stock:item-list')

def sum_list(l):
    t=0
    for i in l:
        t += i
    return t   


def update_stock(request):
    stock = Item.objects.all()
    order_total= {}
    current_stock = {}
    for i in stock:
        item = i.order_set.values_list('quantity',flat=True)
        order_total[i] = item

    for k,v in order_total.items():
        order_total[k] = sum_list(v)
        qte = k.quantity - order_total[k]
        current_stock[k] = qte
            
    return render(request,'stock/update_stock.html',{'current_stock':current_stock})    
       
#///////////////////////////////////////////////////////////////////////////////
class TheCreateView(CreateView):
    
    form_class = TheForm
    queryset = The.objects.all()
    template_name = 'stock/the_create.html'
    
    

    def form_valid(self, form):
        return super().form_valid(form)
        
class  TheListView(ListView):
    model = The
    template_name = 'stock/the_list.html'
    queryset = The.objects.all()

class  TheDetailView(DetailView):
    model = The
    template_name = 'stock/the_detail.html'
    #queryset = The.objects.all()
    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(The, id=id_)

class TheUpdateView(UpdateView):
    model = The
    form_class = TheForm
    template_name = 'stock/the_update_form.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(The, id=id_)
    
    def form_valid(self, form):
        return super().form_valid(form)

#/////////////////////////////////////////////////////////////////////////////////////////////////////
class ParfumCreateView(CreateView):
    form_class = ParfumForm
    model = Parfum
    queryset = Parfum.objects.all()
    template_name = 'stock/parfum_create.html'

    def form_valid(self, form):
        return super().form_valid(form)

class  ParfumDetailView(DetailView):
    model = Parfum
    template_name = 'stock/parfum_detail.html'
    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Parfum, id=id_)
    
class  ParfumListView(ListView):
    model = Parfum
    template_name = 'stock/parfum_list.html'
    queryset = Parfum.objects.all()

class ParfumUpdateView(UpdateView):
    model = Parfum
    form_class = ParfumForm
    template_name = 'stock/parfum_update.html'
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Parfum, id=id_)
    
    def form_valid(self, form):
        return super().form_valid(form)  
#////////////////////////////////////////////////////////////////////////////////////////////



def item_search(request):
    form = ItemSearchForm(request.GET or None)
    items = Item.objects.none()  # Initialize empty QuerySet
    the_items = The.objects.none()
    parfum_items = Parfum.objects.none()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        # Search in Item model
        items = Item.objects.filter(
            Q(item__icontains=query) | 
            Q(description__icontains=query)
        )
        # Search in The model
        the_items = The.objects.filter(
            Q(item__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__icontains=query) |
            Q(packaging__icontains=query) |
            Q(weight__icontains=query) |
            Q(ref__icontains=query)
        )
        # Search in Parfum model
        parfum_items = Parfum.objects.filter(
            Q(item__icontains=query) | 
            Q(description__icontains=query) |
            Q(sub_brand__icontains=query) |
            Q(type__icontains=query) |
            Q(volum__icontains=query)
        )
    
    return render(request, 'stock/item_search.html', {
        'form': form,
        'items': items,
        'the_items': the_items,
        'parfum_items': parfum_items
    })
