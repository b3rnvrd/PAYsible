from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.web import routes as web_routes
from app.api import routers as api_routers

# --- IMPORT DATABASE ---
from app.core.database import engine, Base
# IMPORTANT : On importe les modèles pour que SQLAlchemy les détecte
from app.models import user, account, transaction, beneficiary 

# Création des tables dans paysible.db
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PAYsible App",
    description="Application de paiement modulaire basée sur FastAPI.",
    version="0.1.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key="secretkey",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(web_routes.router)
app.include_router(api_routers.router, prefix="/api")

@app.get("/status")
def get_status():
    return {"status": "OK", "version": app.version}