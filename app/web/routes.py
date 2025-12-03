from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

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
    """
    Page d'accueil principale.
    Si l'utilisateur est connecté, affiche la page home.html avec ses comptes.
    Sinon, affiche la page de landing publique (index.html).
    """
    user_email = None
    if hasattr(request, "session"):
        user_email = request.session.get("user_email")

    # Si l'utilisateur est connecté, afficher la page home avec ses comptes
    if user_email:
        from datetime import datetime
        
        main_account = {
            "id": "ACC001",
            "type": "Compte Courant",
            "balance": "2,450.75",
            "is_main": True
        }
        
        accounts = [
            {
                "id": "ACC001",
                "type": "Compte Courant",
                "balance": "2,450.75",
                "is_main": True
            },
            {
                "id": "ACC002",
                "type": "Compte Épargne",
                "balance": "5,320.00",
                "is_main": False
            },
            {
                "id": "ACC003",
                "type": "Compte Professionnel",
                "balance": "1,890.50",
                "is_main": False
            }
        ]
        
        transactions = [
            {
                "date": "01/12/2025",
                "description": "Salaire",
                "details": "Virement mensuel",
                "account_id": "ACC001",
                "amount": 2500.00,
                "status": "completed",
                "status_label": "Complété"
            },
            {
                "date": "29/11/2025",
                "description": "Supermarché",
                "details": "Carrefour - Courses",
                "account_id": "ACC001",
                "amount": -85.30,
                "status": "completed",
                "status_label": "Complété"
            },
            {
                "date": "28/11/2025",
                "description": "Transfert épargne",
                "details": "Épargne automatique",
                "account_id": "ACC002",
                "amount": 200.00,
                "status": "completed",
                "status_label": "Complété"
            },
            {
                "date": "27/11/2025",
                "description": "Abonnement Netflix",
                "details": "Prélèvement mensuel",
                "account_id": "ACC001",
                "amount": -13.49,
                "status": "completed",
                "status_label": "Complété"
            },
            {
                "date": "26/11/2025",
                "description": "Facture électricité",
                "details": "EDF - Novembre",
                "account_id": "ACC001",
                "amount": -120.00,
                "status": "pending",
                "status_label": "En attente"
            }
        ]
        
        stats = {
            "total_income": "2,500.00",
            "total_expenses": "218.79",
            "transaction_count": 12
        }
        
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        return templates.TemplateResponse(
            "pages/home.html",
            {
                "request": request,
                "user_email": user_email,
                "user_name": user_email.split("@")[0].capitalize(),
                "main_account": main_account,
                "accounts": accounts,
                "transactions": transactions,
                "stats": stats,
                "current_date": current_date
            }
        )
    
    # Sinon, afficher la page de landing publique
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
