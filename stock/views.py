from django.shortcuts import render, redirect
from django.http import HttpRequest

from stock.models import *
from datetime import date
from django.core import validators

#-----------------------------------------------------------------------
# Create your views here.
def index(request):
    return render(request,"stock/index.html",{'index':'Nina Bazar'})

