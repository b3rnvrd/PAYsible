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


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """
    Affiche la page des paramètres utilisateur.
    """
    user_email = None
    if hasattr(request, "session"):
        user_email = request.session.get("user_email")

    # Vérifier si l'utilisateur est connecté
    if not user_email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "pages/settings.html",
        {
            "request": request,
            "title": "Paramètres - PAYsible",
            "user_email": user_email,
        },
    )