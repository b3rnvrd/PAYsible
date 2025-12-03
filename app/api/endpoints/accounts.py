from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import string

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
    created_at: str
    is_active: bool = True

class AccountBalanceResponse(BaseModel):
    account_id: int
    balance: float


# Mock data pour la démo (à remplacer par une vraie base de données)
MOCK_ACCOUNTS = [
    {
        "id": 1,
        "label": "Compte Principal",
        "type": "CHECKING",
        "iban": "FR76 1234 5678 9012 3456 7890 123",
        "created_at": "2024-01-15T10:30:00",
        "is_active": True
    },
    {
        "id": 2,
        "label": "Livret A",
        "type": "SAVINGS",
        "iban": "FR76 9876 5432 1098 7654 3210 987",
        "created_at": "2024-02-20T14:45:00",
        "is_active": True
    }
]

# Mock balances
MOCK_BALANCES = {
    1: 2543.78,
    2: 15678.90
}

next_account_id = 3


def generate_iban():
    """Génère un faux IBAN français pour la démo."""
    numbers = ''.join(random.choices(string.digits, k=23))
    iban = f"FR76 {numbers[:4]} {numbers[4:8]} {numbers[8:12]} {numbers[12:16]} {numbers[16:20]} {numbers[20:23]}"
    return iban


@router.get("/", response_model=List[AccountResponse])
async def get_accounts():
    """
    Lister tous les comptes de l'utilisateur.
    
    Endpoint: GET /api/accounts/
    """
    # Filtrer uniquement les comptes actifs
    return [acc for acc in MOCK_ACCOUNTS if acc["is_active"]]


@router.post("/", response_model=AccountResponse)
async def create_account(account: AccountCreate):
    """
    Ouvrir un compte (Courant ou Épargne).
    
    Endpoint: POST /api/accounts/
    Payload: { "label": "Compte Joint", "type": "CHECKING" }
    """
    global next_account_id
    
    # Validation du type
    if account.type not in ["CHECKING", "SAVINGS"]:
        raise HTTPException(status_code=400, detail="Type de compte invalide. Utilisez CHECKING ou SAVINGS.")
    
    # Créer le nouveau compte
    new_account = {
        "id": next_account_id,
        "label": account.label,
        "type": account.type,
        "iban": generate_iban(),
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    MOCK_ACCOUNTS.append(new_account)
    MOCK_BALANCES[next_account_id] = 0.0
    next_account_id += 1
    
    return new_account


@router.get("/{account_id}/", response_model=AccountResponse)
async def get_account(account_id: int):
    """
    Détails d'un compte (IBAN, Date de création).
    
    Endpoint: GET /api/accounts/{id}/
    """
    account = next((acc for acc in MOCK_ACCOUNTS if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    if not account["is_active"]:
        raise HTTPException(status_code=404, detail="Compte clôturé.")
    
    return account


@router.patch("/{account_id}/", response_model=AccountResponse)
async def update_account(account_id: int, account_update: AccountUpdate):
    """
    Renommer le compte.
    
    Endpoint: PATCH /api/accounts/{id}/
    Payload: { "label": "Nouveau nom" }
    """
    account = next((acc for acc in MOCK_ACCOUNTS if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    if not account["is_active"]:
        raise HTTPException(status_code=404, detail="Compte clôturé.")
    
    # Mettre à jour le label
    account["label"] = account_update.label
    
    return account


@router.delete("/{account_id}/")
async def delete_account(account_id: int):
    """
    Clôturer le compte (Soft delete).
    
    Endpoint: DELETE /api/accounts/{id}/
    """
    account = next((acc for acc in MOCK_ACCOUNTS if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    if not account["is_active"]:
        raise HTTPException(status_code=404, detail="Compte déjà clôturé.")
    
    # Soft delete
    account["is_active"] = False
    
    return {"message": f"Compte {account['label']} clôturé avec succès."}


@router.get("/{account_id}/balance/", response_model=AccountBalanceResponse)
async def get_account_balance(account_id: int):
    """
    Calcul du solde (Agrégation des transactions).
    
    Endpoint: GET /api/accounts/{id}/balance/
    """
    account = next((acc for acc in MOCK_ACCOUNTS if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé.")
    
    if not account["is_active"]:
        raise HTTPException(status_code=404, detail="Compte clôturé.")
    
    balance = MOCK_BALANCES.get(account_id, 0.0)
    
    return {
        "account_id": account_id,
        "balance": balance
    }
