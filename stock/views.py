from django.db.models.base import Model as Model
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from .models import Item
from django.views.generic.list import ListView
from django.views.generic import ( 
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView    
    )

from stock.forms import ItemModelForm
from django.views import View

def dashboard():
    pass



class ItemCreateView(CreateView):
    template_name = 'stock/item_create.html'
    form_class = ItemModelForm
    queryset = Item.objects.all()

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)
    

class  ItemListView(ListView):
    template_name = 'stock/item_list.html'
    queryset = Item.objects.all()   

 

class  ItemDetailView(DetailView):
    template_name = 'stock/item_detail.html'
    queryset = Item.objects.all()
    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Item, id=id_)


class ItemUpdateView(UpdateView):
    #template_name = 'stock/item_create.html'
    form_class = ItemModelForm
    queryset = Item.objects.all()
    #success_url = '/'

    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Item, id=id_)
    
    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class  ItemDeleteView(DeleteView):
    template_name = 'stock/item_delete.html'
    
    def get_object(self):
       id_ = self.kwargs.get("id")
       return get_object_or_404(Item, id=id_)
    def get_success_url(self):
        return reverse('stock:item-list')

