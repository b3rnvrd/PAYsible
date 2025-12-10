from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db

# Modèles
from app.models.beneficiary import (
    BeneficiaryDB, 
    BeneficiaryCreate, 
    BeneficiaryUpdate, 
    BeneficiaryResponse
)
from app.models.account import AccountDB 
from app.models.user import UserDB 

router = APIRouter()

# --- FONCTION UTILITAIRE ---
def get_current_user_from_session(request: Request, db: Session):
    """Récupère l'utilisateur SQL depuis l'email stocké en session."""
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur inconnu")
    return user


# --- ROUTES ---

@router.get("/", response_model=List[BeneficiaryResponse])
def get_beneficiaries(request: Request, db: Session = Depends(get_db)):
    """Récupère uniquement les bénéficiaires des comptes de l'utilisateur connecté."""
    user = get_current_user_from_session(request, db)
    
    # Jointure pour trouver les bénéficiaires liés aux comptes de cet utilisateur
    beneficiaries = (
        db.query(BeneficiaryDB)
        .join(AccountDB)
        .filter(AccountDB.user_id == user.id)
        .all()
    )
    return beneficiaries


@router.post("/", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(
    beneficiary: BeneficiaryCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """Crée un bénéficiaire rattaché au premier compte de l'utilisateur."""
    user = get_current_user_from_session(request, db)
    
    # On cherche un compte auquel rattacher ce bénéficiaire
    # (Simplification : on prend le premier compte trouvé)
    account = db.query(AccountDB).filter(AccountDB.user_id == user.id).first()
    
    if not account:
        raise HTTPException(
            status_code=400, 
            detail="Vous devez avoir au moins un compte bancaire pour ajouter des bénéficiaires."
        )

    # Création
    db_beneficiary = BeneficiaryDB(
        name=beneficiary.name,
        iban=beneficiary.iban,
        account_id=account.id 
    )
    
    db.add(db_beneficiary)
    db.commit()
    db.refresh(db_beneficiary)
    
    return db_beneficiary


@router.patch("/{id}/", response_model=BeneficiaryResponse)
def update_beneficiary(
    id: int, 
    beneficiary_update: BeneficiaryUpdate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Met à jour un bénéficiaire (vérifie l'appartenance)."""
    user = get_current_user_from_session(request, db)
    
    # On cherche le bénéficiaire en vérifiant qu'il appartient bien à un compte de l'user
    db_beneficiary = (
        db.query(BeneficiaryDB)
        .join(AccountDB)
        .filter(BeneficiaryDB.id == id)
        .filter(AccountDB.user_id == user.id)  # Sécurité critique
        .first()
    )
    
    if not db_beneficiary:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé ou accès refusé")
    
    # Mise à jour des champs
    update_data = beneficiary_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_beneficiary, key, value)
    
    db.commit()
    db.refresh(db_beneficiary)
    return db_beneficiary


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(id: int, request: Request, db: Session = Depends(get_db)):
    """Supprime un bénéficiaire (vérifie l'appartenance)."""
    user = get_current_user_from_session(request, db)
    
    db_beneficiary = (
        db.query(BeneficiaryDB)
        .join(AccountDB)
        .filter(BeneficiaryDB.id == id)
        .filter(AccountDB.user_id == user.id)
        .first()
    )
    
    if not db_beneficiary:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé ou accès refusé")
    
    db.delete(db_beneficiary)
    db.commit()
    return None