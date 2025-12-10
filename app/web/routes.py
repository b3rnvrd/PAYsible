# app/web/routes.py
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
import json
import re
from app.core.i18n import get_translator
from app.core.database import get_db
from app.core.dependencies import get_user_email_from_session

# Import des modèles
from app.models.user import UserDB
from app.models.account import AccountDB
from app.models.transaction import TransactionDB, TransactionEntryDB
from app.models.beneficiary import BeneficiaryDB

router = APIRouter(tags=["Web Pages"])
templates = Jinja2Templates(directory="templates")


def get_account_balance(db: Session, account_id: int) -> float:
    balance = db.query(func.sum(TransactionEntryDB.amount)) \
        .filter(TransactionEntryDB.account_id == account_id).scalar()
    return float(balance) if balance else 0.0


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request, db: Session = Depends(get_db)):
    """Page d'accueil avec données réelles."""
    user_email = get_user_email_from_session(request)
    _ = get_translator(request) # Traducteur

    if user_email:
        user = db.query(UserDB).filter(UserDB.email == user_email).first()
        if not user:
            return RedirectResponse(url="/logout")

        accounts_data = []
        total_balance = 0
        main_account_data = None
        db_accounts = user.accounts

        for index, acc in enumerate(db_accounts):
            bal = get_account_balance(db, acc.id)
            acc_info = {
                "id": acc.id,
                "iban": acc.iban,
                "type": acc.type,
                "balance": f"{bal:,.2f}",
                "is_main": (index == 0)
            }
            accounts_data.append(acc_info)
            total_balance += bal

            if index == 0:
                main_account_data = acc_info

        # Transactions groupées par compte
        user_account_ids = [acc.id for acc in user.accounts]
        transactions_by_account = {}

        for account in db_accounts:
            account_entries = db.query(TransactionEntryDB) \
                .join(TransactionDB) \
                .filter(TransactionEntryDB.account_id == account.id) \
                .order_by(TransactionDB.date.desc()) \
                .limit(10).all()

            transactions_list = []
            for entry in account_entries:
                transactions_list.append({
                    "date": entry.transaction.date.strftime("%d/%m/%Y"),
                    "description": entry.transaction.description,
                    "details": entry.description if entry.description != entry.transaction.description else "",
                    "amount": entry.amount,
                    "status": "completed"
                })

            transactions_by_account[account.id] = transactions_list

        # Statistiques du mois en cours
        current_month = datetime.now().month
        current_year = datetime.now().year

        month_entries = db.query(TransactionEntryDB) \
            .join(TransactionDB) \
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
                "transactions_by_account": transactions_by_account,
                "stats": stats_display,
                "current_date": datetime.now().strftime("%d/%m/%Y"),
                "_": _ # Injection
            }
        )

    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "user_email": None,
            "_": _ # Injection
        }
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Page Dashboard détaillée avec graphiques."""
    user_email = get_user_email_from_session(request)
    if not user_email:
        return RedirectResponse(url="/login")
    
    _ = get_translator(request) # Traducteur

    user = db.query(UserDB).filter(UserDB.email == user_email).first()

    current_global_balance = 0.0
    accounts_charts_data = []

    for account in user.accounts:
        balance = get_account_balance(db, account.id)
        current_global_balance += balance

        entries = db.query(TransactionEntryDB) \
            .join(TransactionDB) \
            .filter(TransactionEntryDB.account_id == account.id) \
            .order_by(TransactionDB.date.desc()) \
            .limit(20).all()

        dates = []
        history_values = []
        temp_balance = balance

        for entry in entries:
            dates.append(entry.transaction.date.strftime("%d/%m"))
            history_values.append(temp_balance)
            temp_balance -= entry.amount

        dates.reverse()
        history_values.reverse()

        if not dates:
            dates = [datetime.now().strftime("%d/%m")]
            history_values = [balance]

        accounts_charts_data.append({
            "id": account.id,
            "type": account.type,
            "iban": account.iban,
            "balance": f"{balance:,.2f}",
            "labels": json.dumps(dates),
            "data": json.dumps(history_values)
        })

    user_account_ids = [acc.id for acc in user.accounts]
    expenses = db.query(TransactionEntryDB.description, func.sum(TransactionEntryDB.amount)) \
        .filter(TransactionEntryDB.account_id.in_(user_account_ids), TransactionEntryDB.amount < 0) \
        .group_by(TransactionEntryDB.description) \
        .all()

    pie_labels = [e[0] for e in expenses]
    pie_data = [abs(float(e[1])) for e in expenses]

    accounts_data_json = json.dumps([
        {
            "id": acc["id"],
            "type": acc["type"],
            "iban": acc["iban"],
            "balance": acc["balance"],
            "labels": json.loads(acc["labels"]),
            "data": json.loads(acc["data"])
        }
        for acc in accounts_charts_data
    ])

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "user_email": user.email,
            "total_balance": f"{current_global_balance:,.2f}",
            "accounts_data": accounts_charts_data,
            "accounts_data_json": accounts_data_json,
            "chart_pie_labels": json.dumps(pie_labels),
            "chart_pie_data": json.dumps(pie_data),
            "_": _ # Injection
        }
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    _ = get_translator(request) # Traducteur
    return templates.TemplateResponse(
        "pages/login.html",
        {
            "request": request,
            "user_email": get_user_email_from_session(request),
            "form_email": "",
            "_": _ # Injection
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
        request: Request,
        email: str = Form(...),
        db: Session = Depends(get_db),
):
    _ = get_translator(request) # Traducteur
    email = (email or "").strip().lower()

    if not email or len(email) > 255:
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "title": "Connexion - PAYsible",
                "user_email": get_user_email_from_session(request),
                "form_email": "",
                "error": "Veuillez saisir une adresse e-mail valide.",
                "_": _ # Injection
            },
        )

    user = db.query(UserDB).filter(UserDB.email == email).first()

    if not user:
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "title": "Connexion - PAYsible",
                "user_email": get_user_email_from_session(request),
                "form_email": email,
                "error": "Aucun compte trouvé avec cet e-mail.",
                "_": _ # Injection
            },
        )

    if hasattr(request, "session"):
        request.session["user_email"] = user.email

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    _ = get_translator(request) # Traducteur
    return templates.TemplateResponse(
        "pages/register.html",
        {
            "request": request, 
            "title": "Créer un compte - PAYsible", 
            "error": None,
            "_": _ # Injection
        },
    )


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
        request: Request,
        name: str = Form(""),
        last_name: str = Form(""),
        phone_number: str = Form(""),
        address: str = Form(""),
        email: str = Form(...),
        db: Session = Depends(get_db),
):
    _ = get_translator(request) # Traducteur
    email = (email or "").strip().lower()
    phone_number = (phone_number or "").strip()

    if phone_number:
        pattern = r"^\+[1-9]\d{7,14}$"
        if not re.match(pattern, phone_number):
            return templates.TemplateResponse(
                "pages/register.html",
                {
                    "request": request,
                    "title": "Créer un compte - PAYsible",
                    "error": "Le numéro de téléphone doit être au format international, ex : +33612345678.",
                    "_": _ # Injection
                },
            )


    if not email or len(email) > 255:
        return templates.TemplateResponse(
            "pages/register.html",
            {
                "request": request,
                "title": "Créer un compte - PAYsible",
                "error": "Veuillez saisir une adresse e-mail valide.",
                "_": _ # Injection
            },
        )

    existing = db.query(UserDB).filter(UserDB.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "pages/register.html",
            {
                "request": request,
                "title": "Créer un compte - PAYsible",
                "error": "Un compte existe déjà avec cet e-mail.",
                "_": _ # Injection
            },
        )

    user = UserDB(
        name=(name or "").strip() or None,
        last_name=(last_name or "").strip() or None,
        phone_number=phone_number or None,
        address=(address or "").strip() or None,
        email=email,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        "pages/login.html",
        {
            "request": request,
            "title": "Connexion - PAYsible",
            "user_email": user.email,
            "error": None,
            "info": "Compte créé avec succès.",
            "_": _ # Injection
        },
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/soldes", response_class=HTMLResponse)
async def view_soldes(request: Request, db: Session = Depends(get_db)):
    user_email = get_user_email_from_session(request)
    if not user_email: return RedirectResponse(url="/login")
    
    _ = get_translator(request) # Traducteur

    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    accounts_list = []
    transactions_list = []
    total_balance = 0.0

    if user:
        user_accounts = user.accounts
        for acc in user_accounts:
            bal = get_account_balance(db, acc.id)
            total_balance += bal
            acc.balance = bal
            accounts_list.append(acc)

        entries = db.query(TransactionEntryDB) \
            .join(TransactionDB) \
            .filter(TransactionEntryDB.account_id.in_([a.id for a in user_accounts])) \
            .order_by(TransactionDB.date.desc()).all()

        for entry in entries:
            transactions_list.append({
                "date": entry.transaction.date,
                "label": entry.description,
                "category": entry.type,
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
            "total_balance": total_balance,
            "_": _ # Injection
        }
    )


@router.get("/beneficiaries", response_class=HTMLResponse)
def view_beneficiaries(request: Request):
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    _ = get_translator(request) # Traducteur

    return templates.TemplateResponse(
        "pages/beneficiaries.html",
        {
            "request": request, 
            "user_email": user_email,
            "_": _ # Injection
        }
    )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    user_email = None
    if hasattr(request, "session"):
        user_email = request.session.get("user_email")

    if not user_email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    _ = get_translator(request)

    current_lang = request.cookies.get("language", "fr")

    return templates.TemplateResponse(
        "pages/settings.html",
        {
            "request": request,
            "title": "Paramètres - PAYsible",
            "user_email": user_email,
            "_": _,
            "current_lang": current_lang
        },
    )


@router.get("/virement", response_class=HTMLResponse)
async def virement_page(request: Request, db: Session = Depends(get_db)):
    """Affiche la page de virement."""
    user_email = get_user_email_from_session(request)
    if not user_email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    _ = get_translator(request) # Traducteur

    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    if not user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    accounts_data = []
    for acc in user.accounts:
        balance = get_account_balance(db, acc.id)
        accounts_data.append({
            "id": acc.id,
            "type": acc.type,
            "iban": acc.iban,
            "balance": f"{balance:,.2f}"
        })

    user_account_ids = [acc.id for acc in user.accounts]
    beneficiaries = db.query(BeneficiaryDB).filter(
        BeneficiaryDB.account_id.in_(user_account_ids)
    ).all()
    
    beneficiaries_data = []
    for benef in beneficiaries:
        beneficiaries_data.append({
            "id": benef.id,
            "name": benef.name,
            "iban": benef.iban,
            "account_id": benef.account_id
        })

    return templates.TemplateResponse(
        "pages/virement.html",
        {
            "request": request,
            "user_email": user_email,
            "accounts": accounts_data,
            "beneficiaries": beneficiaries_data,
            "error": None,
            "success": None,
            "_": _ # Injection
        }
    )


@router.post("/virement/interne", response_class=HTMLResponse)
async def virement_interne_submit(
        request: Request,
        db: Session = Depends(get_db),
        compte_debit: int = Form(...),
        compte_credit: int = Form(...),
        montant: float = Form(...),
        description: str = Form("")
):
    """Traite un virement interne."""
    user_email = get_user_email_from_session(request)
    if not user_email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    _ = get_translator(request) # Traducteur

    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    
    accounts_data = []
    for acc in user.accounts:
        balance = get_account_balance(db, acc.id)
        accounts_data.append({
            "id": acc.id,
            "type": acc.type,
            "iban": acc.iban,
            "balance": f"{balance:,.2f}"
        })

    if montant <= 0:
        return templates.TemplateResponse(
            "pages/virement.html",
            {
                "request": request, "user_email": user_email, "accounts": accounts_data,
                "error": "⚠️ Le montant du virement doit être strictement positif.",
                "success": None,
                "_": _ # Injection
            }
        )

    if compte_debit == compte_credit:
        return templates.TemplateResponse(
            "pages/virement.html",
            {
                "request": request, "user_email": user_email, "accounts": accounts_data,
                "error": "🚫 Vous ne pouvez pas effectuer un virement vers le même compte.",
                "success": None,
                "_": _ # Injection
            }
        )

    solde_debit = get_account_balance(db, compte_debit)

    if solde_debit < montant:
        return templates.TemplateResponse(
            "pages/virement.html",
            {
                "request": request, "user_email": user_email, "accounts": accounts_data,
                "error": f"💸 Solde insuffisant. Vous avez {solde_debit:,.2f} € disponibles, mais vous essayez de virer {montant:,.2f} €.",
                "success": None,
                "_": _ # Injection
            }
        )

    transaction_desc = description if description else "Virement interne"
    new_transaction = TransactionDB(
        type="Virement interne",
        amount=montant,
        date=datetime.now(),
        description=transaction_desc
    )
    db.add(new_transaction)
    db.flush()

    db.add(TransactionEntryDB(
        amount=-montant, type="DEBIT", description=transaction_desc,
        account_id=compte_debit, transaction_id=new_transaction.id
    ))
    db.add(TransactionEntryDB(
        amount=montant, type="CREDIT", description=transaction_desc,
        account_id=compte_credit, transaction_id=new_transaction.id
    ))

    db.commit()

    accounts_data_updated = []
    for acc in user.accounts:
        new_balance = get_account_balance(db, acc.id)
        accounts_data_updated.append({
            "id": acc.id, "type": f"Compte {acc.type}", "iban": acc.iban, "balance": f"{new_balance:,.2f}"
        })

    return templates.TemplateResponse(
        "pages/virement.html",
        {
            "request": request,
            "user_email": user_email,
            "accounts": accounts_data_updated,
            "error": None,
            "success": f"✅ Virement interne de {montant:,.2f} € effectué avec succès !",
            "_": _ # Injection
        }
    )


@router.post("/virement/beneficiaire", response_class=HTMLResponse)
async def virement_beneficiaire_submit(
    request: Request,
    compte_debit: int = Form(...),
    beneficiaire_id: int = Form(...),
    montant: float = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Traite un virement vers un bénéficiaire externe (ou interne via IBAN)."""
    user_email = get_user_email_from_session(request)
    if not user_email: return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    _ = get_translator(request) # Traducteur

    user = db.query(UserDB).filter(UserDB.email == user_email).first()

    accounts_data = []
    for acc in user.accounts:
        bal = get_account_balance(db, acc.id)
        accounts_data.append({"id": acc.id, "type": f"Compte {acc.type}", "iban": acc.iban, "balance": f"{bal:,.2f}"})

    user_account_ids = [acc.id for acc in user.accounts]
    beneficiaries = db.query(BeneficiaryDB).filter(BeneficiaryDB.account_id.in_(user_account_ids)).all()
    beneficiaries_data = [{"id": b.id, "name": b.name, "iban": b.iban} for b in beneficiaries]

    context = {
        "request": request, "user_email": user_email,
        "accounts": accounts_data, "beneficiaries": beneficiaries_data,
        "error": None, "success": None, "active_tab": "beneficiaire",
        "_": _ # Injection
    }

    if montant <= 0:
        context["error"] = "⚠️ Le montant doit être supérieur à 0 €."
        return templates.TemplateResponse("pages/virement.html", context)

    solde_debit = get_account_balance(db, compte_debit)
    if solde_debit < montant:
        context["error"] = f"💸 Solde insuffisant. Disponible : {solde_debit:,.2f} €."
        return templates.TemplateResponse("pages/virement.html", context)

    beneficiaire = db.query(BeneficiaryDB).filter(BeneficiaryDB.id == beneficiaire_id).first()
    if not beneficiaire:
        context["error"] = "Bénéficiaire introuvable."
        return templates.TemplateResponse("pages/virement.html", context)

    nom_benef = beneficiaire.name

    label = description if description else f"Virement vers {nom_benef}"
    
    new_txn = TransactionDB(type="Virement", amount=montant, date=datetime.now(), description=label)
    db.add(new_txn)
    db.flush()

    db.add(TransactionEntryDB(
        amount=-montant, type="DEBIT", description=f"Pour : {nom_benef}",
        account_id=compte_debit, transaction_id=new_txn.id
    ))

    compte_destinataire = db.query(AccountDB).filter(AccountDB.iban == beneficiaire.iban).first()
    
    if compte_destinataire:
        db.add(TransactionEntryDB(
            amount=montant, type="CREDIT", description=f"Reçu de : {user.name} {user.last_name}",
            account_id=compte_destinataire.id, transaction_id=new_txn.id
        ))
    
    db.commit()

    updated_accounts = []
    for acc in user.accounts:
        bal = get_account_balance(db, acc.id)
        updated_accounts.append({"id": acc.id, "type": f"Compte {acc.type}", "iban": acc.iban, "balance": f"{bal:,.2f}"})
    
    context["accounts"] = updated_accounts
    context["success"] = f"✅ Virement de {montant:,.2f} € envoyé à {nom_benef} !"
    
    return templates.TemplateResponse("pages/virement.html", context)


@router.get("/test-500")
def test_error_500():
    result = 1 / 0
    return result