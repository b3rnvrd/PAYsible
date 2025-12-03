# app/main.py

from fastapi import FastAPI

# 1. INITIALISATION DE L'APPLICATION
app = FastAPI(
    title="PAYsible App",
    description="Application de paiement modulaire basée sur FastAPI.",
    version="0.1.0",
)

# --- Imports complémentaires ---

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware  # <-- ajout

from app.web import routes as web_routes
from app.api import routers as api_routers

# 2. MIDDLEWARE DE SESSION (pour stocker l'email de l'utilisateur)
# ⚠️ En prod, change la clé secrète par quelque chose de fort et privé.
app.add_middleware(
    SessionMiddleware,
    secret_key="change-me-in-production",
)

# 3. CONFIGURATION DES RESSOURCES STATIQUES + TEMPLATES
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 4. INCLUSION DES ROUTEURS
app.include_router(web_routes.router)
app.include_router(api_routers.router, prefix="/api")

# 5. Endpoint simple de statut
@app.get("/status")
def get_status():
    return {"status": "OK", "version": app.version}



# ... vos imports existants ...
from app.database import engine, Base
# Importez vos modèles pour qu'ils soient reconnus lors de la création
from app.models import orm 

# Créez les tables (à placer avant la définition de 'app = FastAPI(...)')
Base.metadata.create_all(bind=engine)

app = FastAPI(...) 
# ... suite du fichier ...