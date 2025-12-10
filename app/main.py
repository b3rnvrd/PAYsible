from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse  # <--- Ajout de JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# --- Imports de ton application ---
from app.web import routes as web_routes
from app.api import routers as api_routers
from app.core.database import engine, Base
from app.models import user, account, transaction, beneficiary 

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)

# Initialisation de l'App
app = FastAPI(
    title="PAYsible App",
    description="Application de paiement modulaire basée sur FastAPI.",
    version="0.1.0",
)

# Middleware de Session
app.add_middleware(
    SessionMiddleware,
    secret_key="secretkey", # En prod, utilise une variable d'env
)

# Montage des fichiers statiques (CSS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des Templates Jinja2
templates = Jinja2Templates(directory="templates")

# ==========================================
# GESTION DES ERREURS PERSONNALISÉES
# ==========================================

# Gestion des erreurs HTTP (404, 400, 401, etc.)
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    
    # 1. SI C'EST UNE REQUÊTE API -> On renvoie du JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    # 2. SINON (Site Web) -> On renvoie les pages HTML
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", 
            {"request": request}, 
            status_code=404
        )
    
    # Pour toute autre erreur HTTP sur le site (ex: 400, 401...)
    # On peut soit afficher la 500, soit une page générique
    return templates.TemplateResponse(
        "500.html", 
        {"request": request}, 
        status_code=exc.status_code
    )

# Gestion de l'erreur 500 (Erreur Serveur Interne / Crash code)
@app.exception_handler(500)
async def custom_500_handler(request: Request, exc):
    # Les erreurs 500 de l'API doivent aussi être en JSON si possible,
    # mais pour simplifier ici on garde le template global pour les crashs sévères.
    return templates.TemplateResponse(
        "500.html", 
        {"request": request}, 
        status_code=500
    )

# ==========================================
# ROUTEURS
# ==========================================

# 1. Routes Web (HTML)
app.include_router(web_routes.router)

# 2. Routes API (JSON) - Préfixées par /api
app.include_router(api_routers.router, prefix="/api")

# Endpoint de statut simple
@app.get("/status")
def get_status():
    return {"status": "OK", "version": app.version}