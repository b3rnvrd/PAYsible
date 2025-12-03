from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.orm import AccountORM

router = APIRouter(prefix="/accounts", tags=["Comptes"])
templates = Jinja2Templates(directory="templates")

@router.get("/{account_id}")
async def get_account_balance(
    request: Request, 
    account_id: int, 
    db: Session = Depends(get_db) # Injection de la BDD
):
    # Requête SQL via l'ORM
    account = db.query(AccountORM).filter(AccountORM.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé")

    # Calcul du solde via les relations
    transactions_list = [entry.amount for entry in account.entries]
    balance = sum(transactions_list)

    return templates.TemplateResponse(
        "pages/soldes.html",
        {
            "request": request,
            "id": account.id,
            "owner": account.owner.name if account.owner else "Inconnu",
            "type": account.type,
            "transactions": transactions_list,
            # Vous pouvez ajouter 'balance' si votre template HTML l'utilise
        }
    )