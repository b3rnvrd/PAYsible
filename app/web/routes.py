# app/web/routes.py
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
import json

from app.core.database import get_db
from app.core.dependencies import get_user_email_from_session

# Import des modèles
from app.models.user import UserDB
from app.models.account import AccountDB
from app.models.transaction import TransactionDB, TransactionEntryDB

router = APIRouter(tags=["Web Pages"])
templates = Jinja2Templates(directory="templates")

# --- Fonctions Utilitaires ---
def get_account_balance(db: Session, account_id: int) -> float:
    """Calcule le solde d'un compte en agrégeant ses entrées."""
    balance = db.query(func.sum(TransactionEntryDB.amount))\
                .filter(TransactionEntryDB.account_id == account_id).scalar()
    return float(balance) if balance else 0.0

@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request, db: Session = Depends(get_db)):
    """Page d'accueil avec données réelles."""
    user_email = get_user_email_from_session(request)

    if user_email:
        # 1. Récupérer l'utilisateur
        user = db.query(UserDB).filter(UserDB.email == user_email).first()
        if not user:
             return RedirectResponse(url="/logout")

        # 2. Récupérer les comptes et calculer les soldes
        accounts_data = []
        total_balance = 0
        main_account_data = None
        
        # On suppose que le premier compte créé est le principal (ou par type Courant)
        db_accounts = user.accounts
        
        for index, acc in enumerate(db_accounts):
            bal = get_account_balance(db, acc.id)
            acc_info = {
                "id": acc.id, # On garde l'ID numérique ou on formate
                "iban": acc.iban,
                "type": f"Compte {acc.type}",
                "balance": f"{bal:,.2f}",
                "is_main": (index == 0) # Le premier est principal par défaut
            }
            accounts_data.append(acc_info)
            total_balance += bal
            
            if index == 0:
                main_account_data = acc_info

        # 3. Récupérer les transactions récentes (via TransactionEntry)
        # On récupère les entrées liées aux comptes de l'utilisateur
        user_account_ids = [acc.id for acc in user.accounts]
        
        recent_entries = db.query(TransactionEntryDB)\
            .join(TransactionDB)\
            .filter(TransactionEntryDB.account_id.in_(user_account_ids))\
            .order_by(TransactionDB.date.desc())\
            .limit(5).all()

        transactions_data = []
        for entry in recent_entries:
            transactions_data.append({
                "date": entry.transaction.date.strftime("%d/%m/%Y"),
                "description": entry.transaction.description,
                "details": entry.description if entry.description != entry.transaction.description else "",
                "account_id": entry.account_id,
                "amount": entry.amount,
                "status": "completed"
            })

        # 4. Calculer les statistiques du mois en cours
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        month_entries = db.query(TransactionEntryDB)\
            .join(TransactionDB)\
            .filter(
                TransactionEntryDB.account_id.in_(user_account_ids),
                extract('month', TransactionDB.date) == current_month,
                extract('year', TransactionDB.date) == current_year
            ).all()

        stats = {
            "total_income": sum(e.amount for e in month_entries if e.amount > 0),
            "total_expenses": sum(e.amount for e in month_entries if e.amount < 0),
            "transaction_count": len(month_entries)
        }
        
        # Formatage pour l'affichage
        stats_display = {
            "total_income": f"{stats['total_income']:,.2f}",
            "total_expenses": f"{stats['total_expenses']:,.2f}",
            "transaction_count": stats['transaction_count']
        }

        return templates.TemplateResponse(
            "pages/home.html",
            {
                "request": request,
                "user_email": user.email,
                "user_name": user.name,
                "main_account": main_account_data,
                "accounts": accounts_data,
                "transactions": transactions_data,
                "stats": stats_display,
                "current_date": datetime.now().strftime("%d/%m/%Y")
            }
        )
    
    return templates.TemplateResponse("index.html", {"request": request, "user_email": None})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Page Dashboard complète avec graphiques."""
    user_email = get_user_email_from_session(request)
    if not user_email:
        return RedirectResponse(url="/login")

    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    user_account_ids = [acc.id for acc in user.accounts]

    # --- KPI 1: Dépenses par Catégorie (basé sur la description) ---
    # On prend toutes les dépenses (montant < 0)
    expenses = db.query(TransactionEntryDB.description, func.sum(TransactionEntryDB.amount))\
        .filter(TransactionEntryDB.account_id.in_(user_account_ids), TransactionEntryDB.amount < 0)\
        .group_by(TransactionEntryDB.description)\
        .all()
    
    # Préparation données Chart.js (Doughnut)
    labels_pie = [e[0] for e in expenses]
    data_pie = [abs(float(e[1])) for e in expenses] # On met en positif pour le graph

    # --- KPI 2: Evolution du Solde (Simulation simple) ---
    # Pour faire simple, on prend les 10 dernières transactions et on simule l'évolution inverse
    # depuis le solde actuel.
    current_global_balance = sum(get_account_balance(db, acc.id) for acc in user.accounts)
    
    last_transactions = db.query(TransactionEntryDB)\
        .join(TransactionDB)\
        .filter(TransactionEntryDB.account_id.in_(user_account_ids))\
        .order_by(TransactionDB.date.desc())\
        .limit(20).all() # 20 derniers mouvements
    
    balance_history = []
    dates_history = []
    temp_balance = current_global_balance

    # On remonte le temps
    for entry in last_transactions:
        balance_history.append(temp_balance)
        dates_history.append(entry.transaction.date.strftime("%d/%m"))
        temp_balance -= entry.amount # On inverse l'opération pour retrouver l'état précédent

    # On remet dans l'ordre chronologique
    balance_history.reverse()
    dates_history.reverse()

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "user_email": user.email,
            "chart_pie_labels": json.dumps(labels_pie),
            "chart_pie_data": json.dumps(data_pie),
            "chart_line_labels": json.dumps(dates_history),
            "chart_line_data": json.dumps(balance_history),
            "total_balance": f"{current_global_balance:,.2f}"
        }
    )

# ... (Gardez les routes login, logout, settings existantes telles quelles) ...

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request, "user_email": get_user_email_from_session(request)})

@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, email: str = Form(...)):
    email = email.strip()
    if not email:
        return templates.TemplateResponse("pages/login.html", {"request": request, "error": "Email requis"})
    request.session["user_email"] = email
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    user_email = get_user_email_from_session(request)
    if not user_email: return RedirectResponse(url="/login")
    return templates.TemplateResponse("pages/settings.html", {"request": request, "user_email": user_email})

@router.get("/soldes", response_class=HTMLResponse)
async def view_soldes(request: Request, db: Session = Depends(get_db)):
    """Affiche les soldes avec les données réelles (mis à jour)."""
    user_email = get_user_email_from_session(request)
    if not user_email: return RedirectResponse(url="/login")

    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    accounts_list = []
    transactions_list = []
    total_balance = 0.0

    if user:
        # On doit construire des objets ou dicts car AccountDB n'a pas .balance
        user_accounts = user.accounts
        for acc in user_accounts:
            bal = get_account_balance(db, acc.id)
            total_balance += bal
            
            # On crée un objet "proxy" ou on injecte l'attribut dynamiquement
            acc.balance = bal # Injection python dynamique pour le template
            accounts_list.append(acc)

        # Récup transactions via TransactionEntry
        entries = db.query(TransactionEntryDB)\
            .join(TransactionDB)\
            .filter(TransactionEntryDB.account_id.in_([a.id for a in user_accounts]))\
            .order_by(TransactionDB.date.desc()).all()
            
        for entry in entries:
            # On adapte pour le template soldes.html existant
            transactions_list.append({
                "date": entry.transaction.date,
                "label": entry.description,
                "category": entry.type, # CREDIT/DEBIT ou le type de la TransactionDB
                "amount": entry.amount
            })

    return templates.TemplateResponse(
        "pages/soldes.html",
        {
            "request": request,
            "user_email": user_email,
            "user_name": user.name if user else "",
            "accounts": accounts_list,
            "transactions": transactions_list,
            "total_balance": total_balance
        }
    )

@router.get("/beneficiaries", response_class=HTMLResponse)
def view_beneficiaries(request: Request):
    user_email = get_user_email_from_session(request)
    if not user_email: return RedirectResponse(url="/login")
    return templates.TemplateResponse("pages/beneficiaries.html", {"request": request, "user_email": user_email})