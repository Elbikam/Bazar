from django.shortcuts import render
from django.http import HttpRequest
import random
from stock.models import Barcode
from stock.forms import BarcodeForm
import barcode
from barcode.writer import ImageWriter


# Create your views here.
def index(request):
    return render(request,"stock/index.html",{'index':'Nina Bazar'})



    
