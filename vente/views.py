from django.shortcuts import render, redirect
from vente.models import *

# Create your views here.
def index(request):
    return render(request,"vente/index_vente.html",{'index':'Nina Bazar'})
