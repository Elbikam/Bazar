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
from .forms import TheForm, ParfumForm
from sale.models import Sale,Order
from collections import defaultdict


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


def update_stock(request):
    stock = {}
    orders_totals = defaultdict(int)
    orders = Order.objects.values('item_id_id', 'quantity')
    for o in orders:
        orders_totals[o['item_id_id']] += o['quantity']
    
    for k,v in orders_totals.items():
        item = Item.objects.get(id=k)
        qte = item.quantity - v
        stock[item] = qte

       
    return render(request,'stock/update_stock.html',{'stock':stock})    
       















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

