from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

# 1. On importe la session de DB
from app.core.database import get_db

# 2. On importe les Modèles SQL (DB) et Pydantic (Schemas)
from app.models.beneficiary import (
    BeneficiaryDB, 
    BeneficiaryCreate, 
    BeneficiaryUpdate, 
    BeneficiaryResponse
)
# On a besoin du modèle Account pour rattacher le bénéficiaire à un compte existant
from app.models.account import AccountDB 

router = APIRouter()

# --- ROUTES ---

@router.get("/", response_model=List[BeneficiaryResponse])
def get_beneficiaries(db: Session = Depends(get_db)):
    """Récupère tous les bénéficiaires dans la base de données SQL."""
    return db.query(BeneficiaryDB).all()

@router.post("/", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary: BeneficiaryCreate, db: Session = Depends(get_db)):
    """Ajoute un bénéficiaire dans la base de données."""
    
    # --- LOGIQUE TEMPORAIRE (En attendant l'Authentification) ---
    # Un bénéficiaire doit appartenir à un compte.
    # Comme on n'est pas encore logué, on va tout rattacher au compte ID 1.
    
    # 1. Vérifier si le compte ID 1 existe, sinon le créer pour éviter un crash
    account = db.query(AccountDB).filter(AccountDB.id == 1).first()
    if not account:
        # On crée un compte "fictif" pour le développement
        # Note: Idéalement il faudrait aussi un User ID 1, mais SQLite est permissif par défaut
        fake_account = AccountDB(id=1, type="Courant", iban="FR76DEFAULTUSER", user_id=1)
        db.add(fake_account)
        db.commit()

    # 2. Création du bénéficiaire
    # On utilise les données reçues (name, iban) et on force l'account_id à 1
    db_beneficiary = BeneficiaryDB(
        name=beneficiary.name,
        iban=beneficiary.iban,
        account_id=1 
    )
    
    db.add(db_beneficiary)     # Ajouter à la session
    db.commit()                # Sauvegarder en DB
    db.refresh(db_beneficiary) # Recharger pour avoir l'ID généré et l'account_id
    
    return db_beneficiary

@router.patch("/{id}/", response_model=BeneficiaryResponse)
def update_beneficiary(id: int, beneficiary_update: BeneficiaryUpdate, db: Session = Depends(get_db)):
    """Met à jour un bénéficiaire existant."""
    # 1. Chercher en DB
    db_beneficiary = db.query(BeneficiaryDB).filter(BeneficiaryDB.id == id).first()
    
    if not db_beneficiary:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    
    # 2. Mettre à jour uniquement les champs fournis
    update_data = beneficiary_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_beneficiary, key, value)
    
    db.commit()
    db.refresh(db_beneficiary)
    return db_beneficiary

@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(id: int, db: Session = Depends(get_db)):
    """Supprime un bénéficiaire de la DB."""
    db_beneficiary = db.query(BeneficiaryDB).filter(BeneficiaryDB.id == id).first()
    
    if not db_beneficiary:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    
    db.delete(db_beneficiary)
    db.commit()
    return None