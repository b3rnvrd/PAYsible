# app/web/routes.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 1. INITIALISATION DE L'APIRouter
router = APIRouter(
    tags=["Web Pages"]
)

# NOTE: Dans ce modèle, le moteur Jinja2 est initialisé dans main.py.
# Pour le rendre disponible ici (sans refactorisation avancée), on peut 
# soit le réinitialiser, soit le passer en dépendance. 
# Pour l'instant, on va simuler l'accès pour garder les choses simples.

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    # Pour que cela fonctionne, vous devez aussi avoir un fichier templates/index.html
    return templates.TemplateResponse("index.html", {"request": request, "title": "Accueil PAYsible"})