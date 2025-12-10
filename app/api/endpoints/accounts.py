from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import string

from app.core.database import get_db
from app.core.dependencies import get_current_user_from_session
from app.models.account import AccountDB
from app.models.user import UserDB
from app.models.transaction import TransactionEntryDB

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

# Schémas Pydantic
class AccountCreate(BaseModel):
    label: str
    type: str  # CHECKING ou SAVINGS

class AccountUpdate(BaseModel):
    label: str

class AccountResponse(BaseModel):
    id: int
    label: str
    type: str
    iban: str
    created_at: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True

class AccountBalanceResponse(BaseModel):
    account_id: int
    balance: float


def generate_iban():
    """Génère un faux IBAN français pour la démo."""
    numbers = ''.join(random.choices(string.digits, k=23))
    iban = f"FR76 {numbers[:4]} {numbers[4:8]} {numbers[8:12]} {numbers[12:16]} {numbers[16:20]} {numbers[20:23]}"
    return iban


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(request: Request, db: Session = Depends(get_db)):
    """
    Lister tous les comptes de l'utilisateur.
    
    Endpoint: GET /api/accounts/
    """
    # Récupérer l'utilisateur depuis la session
    user = get_current_user_from_session(request, db)
    
    # Filtrer les comptes par l'utilisateur connecté
    accounts = db.query(AccountDB).filter(AccountDB.user_id == user.id).all()
    
    # Créer la réponse avec les champs nécessaires
    result = []
    for acc in accounts:
        result.append(AccountResponse(
            id=acc.id,
            label=f"Compte {acc.type}",  # Label générique basé sur le type
            type=acc.type,
            iban=acc.iban,
            created_at=datetime.now().isoformat(),  # Pas de champ created_at dans la DB
            is_active=True
        ))
    
    return result


@router.post("/", response_model=AccountResponse)
async def create_account(account: AccountCreate, request: Request, db: Session = Depends(get_db)):
    """
    Ouvrir un compte (Courant ou Épargne).
    
    Endpoint: POST /api/accounts/
    Payload: { "label": "Compte Joint", "type": "CHECKING" }
    """
    # Récupérer l'utilisateur depuis la session
    user = get_current_user_from_session(request, db)
    
    # Validation du type
    if account.type not in ["CHECKING", "SAVINGS", "Courant", "Epargne"]:
        raise HTTPException(
            status_code=400, 
            detail="Type de compte invalide. Utilisez CHECKING, SAVINGS, Courant ou Epargne."
        )
    
    # Normaliser le type
    account_type = account.type
    if account.type == "CHECKING":
        account_type = "Courant"
    elif account.type == "SAVINGS":
        account_type = "Epargne"
    
    # Créer le nouveau compte pour l'utilisateur connecté
    new_account = AccountDB(
        type=account_type,
        iban=generate_iban(),
        user_id=user.id  # Utiliser l'ID de l'utilisateur connecté
    )
    
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return AccountResponse(
        id=new_account.id,
        label=account.label,
        type=account.type,  # Retourner le type demandé (CHECKING/SAVINGS)
        iban=new_account.iban,
        created_at=datetime.now().isoformat(),
        is_active=True
    )


@router.get("/{account_id}/", response_model=AccountResponse)
async def get_account(account_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Détails d'un compte (IBAN, Date de création).
    
    Endpoint: GET /api/accounts/{id}/
    """
    # Récupérer l'utilisateur depuis la session
    user = get_current_user_from_session(request, db)
    
    account = db.query(AccountDB).filter(
        AccountDB.id == account_id,
        AccountDB.user_id == user.id  # Vérifier que le compte appartient à l'utilisateur
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    # Convertir le type de la DB vers le format API
    api_type = "CHECKING" if account.type == "Courant" else "SAVINGS"
    
    return AccountResponse(
        id=account.id,
        label=f"Compte {account.type}",
        type=api_type,
        iban=account.iban,
        created_at=datetime.now().isoformat(),
        is_active=True
    )


@router.patch("/{account_id}/", response_model=AccountResponse)
async def update_account(account_id: int, account_update: AccountUpdate, request: Request, db: Session = Depends(get_db)):
    """
    Renommer le compte.
    
    Endpoint: PATCH /api/accounts/{id}/
    Payload: { "label": "Nouveau nom" }
    """
    # Récupérer l'utilisateur depuis la session
    user = get_current_user_from_session(request, db)
    
    account = db.query(AccountDB).filter(
        AccountDB.id == account_id,
        AccountDB.user_id == user.id  # Vérifier que le compte appartient à l'utilisateur
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    # Note: La table accounts n'a pas de champ 'label' dans paysible.db
    # On ne peut que retourner le compte avec le nouveau label en mémoire
    # Pour une vraie implementation, il faudrait ajouter une colonne 'label' à la table
    
    api_type = "CHECKING" if account.type == "Courant" else "SAVINGS"
    
    return AccountResponse(
        id=account.id,
        label=account_update.label,  # Le label n'est pas sauvegardé en DB
        type=api_type,
        iban=account.iban,
        created_at=datetime.now().isoformat(),
        is_active=True
    )


@router.delete("/{account_id}/")
async def delete_account(account_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Clôturer le compte (Suppression).
    
    Endpoint: DELETE /api/accounts/{id}/
    """
    # Récupérer l'utilisateur depuis la session
    user = get_current_user_from_session(request, db)
    
    account = db.query(AccountDB).filter(
        AccountDB.id == account_id,
        AccountDB.user_id == user.id  # Vérifier que le compte appartient à l'utilisateur
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    # Suppression du compte (pas de soft delete dans la table actuelle)
    label = f"Compte {account.type}"
    db.delete(account)
    db.commit()
    
    return {"message": f"{label} clôturé avec succès."}


@router.get("/{account_id}/balance/", response_model=AccountBalanceResponse)
async def get_account_balance(account_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Calcul du solde (Agrégation des transactions).
    
    Endpoint: GET /api/accounts/{id}/balance/
    """
    # Récupérer l'utilisateur depuis la session
    user = get_current_user_from_session(request, db)
    
    account = db.query(AccountDB).filter(
        AccountDB.id == account_id,
        AccountDB.user_id == user.id  # Vérifier que le compte appartient à l'utilisateur
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    # Calculer le solde en agrégeant les transaction_entries
    balance_result = db.query(
        func.sum(TransactionEntryDB.amount)
    ).filter(
        TransactionEntryDB.account_id == account_id
    ).scalar()
    
    balance = float(balance_result) if balance_result else 0.0
    
    return AccountBalanceResponse(
        account_id=account_id,
        balance=balance
    )
