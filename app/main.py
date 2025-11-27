# app/main.py

from fastapi import FastAPI
# L'importation de FastAPI doit être en haut.

# 1. INITIALISATION DE L'APPLICATION (C'EST LA LIGNE CLÉ)
app = FastAPI(
    title="PAYsible App",
    description="Application de paiement modulaire basée sur FastAPI.",
    version="0.1.0",
)

# --- Le reste des imports et des configurations peut venir après ---

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.web import routes as web_routes
from app.api import routers as api_routers

# CONFIGURATION DES RESSOURCES
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# INCLUSION DES ROUTEURS
app.include_router(web_routes.router)
app.include_router(api_routers.router, prefix="/api")

@app.get("/status")
def get_status():
    return {"status": "OK", "version": app.version}