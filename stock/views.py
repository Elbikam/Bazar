from django.views.generic import View
from django.shortcuts import render, redirect
from stock.forms import ItemForm,TheForm,ParfumForm,ItemSearchForm
from stock.models import Item,The,Parfum
from django.db import transaction
from django.urls import reverse
from django.views.generic import (DetailView)
from django.views.generic import TemplateView
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from abc import ABC, abstractmethod
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from decimal import Decimal, InvalidOperation,getcontext


#////////////////////////// Item ////////////////////////////////////
class ItemCreate(View):
    template_name = 'stock/item_form.html'
    def get(self, request, *args, **kwargs):
        item_form = ItemForm()
        context = {
            'item_form': item_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        item_form = ItemForm(request.POST)
        if item_form.is_valid():
            with transaction.atomic():
                # Create the item instance from the form but don't save it yet
                item = item_form.save(commit=False)
                # Save the item
                item.save()
                # Redirect to the item detail view
                return redirect(reverse('stock:item-detail', kwargs={'pk': item.pk}))            
        # If form is invalid, return the form with errors
        context = {
            'item_form': item_form,
        }
        return render(request, self.template_name, context)
    
class ItemDetailView(DetailView):
    model = Item
    template_name = 'stock/item_detail.html'
    context_object_name = 'item'  # This is the name you'll use in the template

#////////////////////////// Search Item ////////////////////////////////////
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
#//////////////////////////////// Alert /////////////////////////////////////
def alert_stock(request):
    alert = []
    items = Item.objects.all()
    for i in items:
        if i.quantity < i.alert_qte:
            alert.append(i)
            
    return render(request,'stock/item_alert.html',{'alert':alert}) 
#//////////////////////////// The ////////////////////////////////////////////
class TheCreate(View):
    template_name = 'stock/the_form.html'
    def get(self, request, *args, **kwargs):
        the_form = TheForm()
        context = {
            'the_form': the_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        the_form = TheForm(request.POST)
        if the_form.is_valid():
            with transaction.atomic():
                # Create the item instance from the form but don't save it yet
                the = the_form.save(commit=False)
                # Save the item
                the.save()
                # Redirect to the item detail view  
                return redirect(reverse('stock:the-detail', kwargs={'pk': the.pk}))            
        # If form is invalid, return the form with errors
        context = {
            'the_form': the_form,
        }
        return render(request, self.template_name, context)
class TheDetailView(DetailView):
    model = The
    template_name = 'stock/the_detail.html'
    context_object_name = 'the'  # This is the name you'll use in the template   

#/////////////////////////// Parfum ////////////////////////////////   
class ParfumCreate(View):
    template_name = 'stock/parfum_form.html'
    def get(self, request, *args, **kwargs):
        parfum_form = ParfumForm
        context = {
            'parfum_form': parfum_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        parfum_form = ParfumForm(request.POST)
        if parfum_form.is_valid():
            with transaction.atomic():
                # Create the item instance from the form but don't save it yet
                parfum = parfum_form.save(commit=False)
                # Save the item
                parfum.save()
                # Redirect to the item detail view
                return redirect(reverse('stock:parfum-detail', kwargs={'pk': parfum.pk}))            
        # If form is invalid, return the form with errors
        context = {
            'parfum_form': parfum_form,
        }
        return render(request, self.template_name, context)
class ParfumDetailView(DetailView):
    model = Parfum
    template_name = 'stock/parfum_detail.html'
    context_object_name = 'parfum'  # This is the name you'll use in the template   
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////