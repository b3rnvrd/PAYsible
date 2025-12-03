from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi.templating import Jinja2Templates
from datetime import datetime

# 1. INITIALISATION DE L'APIRouter
router = APIRouter(
    tags=["Web Pages"]
)

# NOTE: Dans ce modèle, le moteur Jinja2 est initialisé dans main.py.
# Pour le rendre disponible ici (sans refactorisation avancée), on peut 
# soit le réinitialiser, soit le passer en dépendance. 
# Pour l'instant, on va simuler l'accès pour garder les choses simples.

templates = Jinja2Templates(directory="templates")

# --- Simulation de données (Fake DB) ---
fake_user_data = {
    "accounts": [
        {"id": 1, "type": "Compte Courant", "iban": "FR76 1234 5678 9012", "balance": 1250.50, "currency": "€"},
        {"id": 2, "type": "Livret A", "iban": "FR76 9876 5432 1098", "balance": 5000.00, "currency": "€"},
    ],
    "transactions": [
        {"id": 1, "date": datetime(2025, 10, 25), "label": "Supermarché", "amount": -150.20, "category": "Alimentation",
         "account_id": 1},
        {"id": 2, "date": datetime(2024, 10, 26), "label": "Virement Maman", "amount": 50.00, "category": "Virement",
         "account_id": 1},
        {"id": 3, "date": datetime(2023, 10, 27), "label": "Abonnement Netflix", "amount": -15.99,
         "category": "Loisirs", "account_id": 1},
        {"id": 4, "date": datetime(2022, 10, 28), "label": "Salaire", "amount": 2500.00, "category": "Revenu",
         "account_id": 1},
        {"id": 5, "date": datetime(2021, 10, 29), "label": "Retrait DAB", "amount": -50.00, "category": "Espèces",
         "account_id": 1},
    ]
}


# --- Routes ---

@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """
    Page d'accueil principale.
    On récupère l'email stocké en session (si présent) pour éventuellement personnaliser la page.
    """
    user_email = None
    if hasattr(request, "session"):
        user_email = request.session.get("user_email")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Accueil PAYsible",
            "user_email": user_email,
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Affiche le formulaire de connexion : saisie de l'adresse e-mail uniquement.
    """
    user_email = None
    if hasattr(request, "session"):
        user_email = request.session.get("user_email")

    return templates.TemplateResponse(
        "pages/login.html",
        {
            "request": request,
            "title": "Connexion - PAYsible",
            "user_email": user_email,
            "error": None,
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, email: str = Form(...)):
    """
    Traite la soumission du formulaire de login.
    - Si email vide → on réaffiche la page avec un message d'erreur.
    - Sinon → on stocke l'email en session puis on redirige vers l'accueil.
    """
    email = email.strip()

    if not email:
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "title": "Connexion - PAYsible",
                "user_email": "",
                "error": "Veuillez saisir une adresse e-mail.",
            },
        )

    # Stockage de l'email dans la session (auth simplifiée)
    if hasattr(request, "session"):
        request.session["user_email"] = email

    # Redirection vers la page d'accueil après connexion
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    """
    Déconnecte l'utilisateur en vidant la session.
    """
    if hasattr(request, "session"):
        request.session.clear()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/soldes", response_class=HTMLResponse, name="view_soldes")
async def view_soldes(request: Request):
    user_email = None
    if hasattr(request, "session"):
        user_email = request.session.get("user_email")

    total_balance = sum(acc["balance"] for acc in fake_user_data["accounts"])

    return templates.TemplateResponse(
        "pages/soldes.html",
        {
            "request": request,
            "user_email": user_email,
            "accounts": fake_user_data["accounts"],
            "transactions": sorted(fake_user_data["transactions"], key=lambda x: x["date"], reverse=True),
            "total_balance": total_balance,
            "title": "Mes Comptes"
        }
    )