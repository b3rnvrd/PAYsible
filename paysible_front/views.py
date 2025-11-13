from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return HttpResponse("""
        <h1>Bienvenue sur PAYsible !</h1>
        <p>Votre projet Django est bien configuré.</p>
        <p>Backend: paysible_back</p>
        <p>Frontend: paysible_front</p>
    """)