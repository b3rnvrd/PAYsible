from django.shortcuts import render

# Create your views here.

def index(request):
    """Vue pour la page d'accueil"""
    return render(request, 'index.html')
