# app/api/endpoints/payments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user_from_session
from app.models.user import UserDB
from app.models.account import AccountDB
from app.models.transaction import TransactionDB, TransactionEntryDB
from app.models.beneficiary import BeneficiaryDB
from sqlalchemy import func

router = APIRouter(prefix="/virements", tags=["Virements"])


# Schemas Pydantic
class VirementInterneRequest(BaseModel):
    compte_debit: int = Field(..., description="ID du compte à débiter")
    compte_credit: int = Field(..., description="ID du compte à créditer")
    montant: float = Field(..., gt=0, description="Montant du virement (doit être > 0)")
    description: Optional[str] = Field("", description="Description optionnelle")


class VirementBeneficiaireRequest(BaseModel):
    compte_debit: int = Field(..., description="ID du compte à débiter")
    beneficiaire_id: int = Field(..., description="ID du bénéficiaire")
    montant: float = Field(..., gt=0, description="Montant du virement (doit être > 0)")
    description: Optional[str] = Field("", description="Description optionnelle")


class VirementResponse(BaseModel):
    success: bool
    message: str
    transaction_id: Optional[int] = None
    nouveau_solde: Optional[float] = None


def get_account_balance(db: Session, account_id: int) -> float:
    """Calcule le solde d'un compte."""
    balance = db.query(func.sum(TransactionEntryDB.amount)) \
        .filter(TransactionEntryDB.account_id == account_id).scalar()
    return float(balance) if balance else 0.0


@router.post("/interne", response_model=VirementResponse)
async def virement_interne(
    data: VirementInterneRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user_from_session)
):
    """
    Effectue un virement entre deux comptes du même utilisateur.
    """
    # Vérifier que les comptes appartiennent bien à l'utilisateur
    compte_debit = db.query(AccountDB).filter(
        AccountDB.id == data.compte_debit,
        AccountDB.user_id == current_user.id
    ).first()
    
    compte_credit = db.query(AccountDB).filter(
        AccountDB.id == data.compte_credit,
        AccountDB.user_id == current_user.id
    ).first()
    
    if not compte_debit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte à débiter introuvable ou non autorisé"
        )
    
    if not compte_credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte à créditer introuvable ou non autorisé"
        )
    
    # Vérifier que ce ne sont pas les mêmes comptes
    if data.compte_debit == data.compte_credit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas effectuer un virement vers le même compte"
        )
    
    # Vérifier le solde
    solde_debit = get_account_balance(db, data.compte_debit)
    if solde_debit < data.montant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solde insuffisant. Disponible: {solde_debit:.2f} €"
        )
    
    # Créer la transaction
    transaction_desc = data.description if data.description else "Virement interne"
    new_transaction = TransactionDB(
        type="Virement interne",
        amount=data.montant,
        date=datetime.now(),
        description=transaction_desc
    )
    db.add(new_transaction)
    db.flush()
    
    # Créer les entrées comptables
    # Débit
    db.add(TransactionEntryDB(
        amount=-data.montant,
        type="DEBIT",
        description=transaction_desc,
        account_id=data.compte_debit,
        transaction_id=new_transaction.id
    ))
    
    # Crédit
    db.add(TransactionEntryDB(
        amount=data.montant,
        type="CREDIT",
        description=transaction_desc,
        account_id=data.compte_credit,
        transaction_id=new_transaction.id
    ))
    
    db.commit()
    db.refresh(new_transaction)
    
    # Calculer le nouveau solde
    nouveau_solde = get_account_balance(db, data.compte_debit)
    
    return VirementResponse(
        success=True,
        message=f"Virement de {data.montant:.2f} € effectué avec succès",
        transaction_id=new_transaction.id,
        nouveau_solde=nouveau_solde
    )


@router.post("/beneficiaire", response_model=VirementResponse)
async def virement_beneficiaire(
    data: VirementBeneficiaireRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user_from_session)
):
    """
    Effectue un virement vers un bénéficiaire enregistré.
    Gère intelligemment les virements internes entre utilisateurs.
    """
    # 1. Vérifier que le compte à débiter appartient bien à l'utilisateur
    compte_debit = db.query(AccountDB).filter(
        AccountDB.id == data.compte_debit,
        AccountDB.user_id == current_user.id
    ).first()
    
    if not compte_debit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte à débiter introuvable ou non autorisé"
        )
    
    # 2. Vérifier que le bénéficiaire existe et est lié à un compte de l'utilisateur
    # On fait une jointure pour s'assurer que le bénéficiaire appartient bien à l'utilisateur courant
    beneficiaire = db.query(BeneficiaryDB).join(AccountDB).filter(
        BeneficiaryDB.id == data.beneficiaire_id,
        AccountDB.user_id == current_user.id
    ).first()
    
    if not beneficiaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bénéficiaire introuvable ou n'appartient pas à vos comptes"
        )
    
    # 3. Vérifier le solde
    solde_debit = get_account_balance(db, data.compte_debit)
    if solde_debit < data.montant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solde insuffisant. Disponible: {solde_debit:.2f} €"
        )
    
    # 4. Créer la transaction globale
    transaction_desc = data.description if data.description else f"Virement vers {beneficiaire.name}"
    new_transaction = TransactionDB(
        type="Virement", # Type générique
        amount=data.montant,
        date=datetime.now(),
        description=transaction_desc
    )
    db.add(new_transaction)
    db.flush()
    
    # 5. Créer l'entrée comptable DEBIT (L'argent part)
    db.add(TransactionEntryDB(
        amount=-data.montant,
        type="DEBIT",
        description=f"Pour : {beneficiaire.name}",
        account_id=data.compte_debit,
        transaction_id=new_transaction.id
    ))

    # --- 6. INTELLIGENCE COMPTABLE : CRÉDIT ---
    # On vérifie si l'IBAN du bénéficiaire correspond à un compte LOCAL dans notre banque
    compte_destinataire = db.query(AccountDB).filter(AccountDB.iban == beneficiaire.iban).first()

    if compte_destinataire:
        # C'est un virement interne déguisé ! On CRÉDITE le compte du destinataire.
        db.add(TransactionEntryDB(
            amount=data.montant,
            type="CREDIT",
            description=f"Reçu de : {current_user.name} {current_user.last_name}",
            account_id=compte_destinataire.id,
            transaction_id=new_transaction.id
        ))
    else:
        # C'est un vrai virement externe (hors banque), l'argent sort simplement du système.
        pass
    
    db.commit()
    db.refresh(new_transaction)
    
    # Calculer le nouveau solde pour le retour API
    nouveau_solde = get_account_balance(db, data.compte_debit)
    
    return VirementResponse(
        success=True,
        message=f"Virement de {data.montant:.2f} € vers {beneficiaire.name} effectué avec succès",
        transaction_id=new_transaction.id,
        nouveau_solde=nouveau_solde
    )