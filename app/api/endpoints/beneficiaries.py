# Fichier: app/api/endpoints/beneficiaries.py

from fastapi import APIRouter, HTTPException, status
from typing import List

# --- IMPORT DES MODÈLES ---
# On va chercher les classes qu'on vient de créer dans le dossier models
from app.models.beneficiary import (
    BeneficiaryCreate, 
    BeneficiaryUpdate, 
    BeneficiaryResponse
)

router = APIRouter()

# --- Simulation Base de Données ---
fake_beneficiaries_db = [
    {"id": 1, "name": "Maman", "iban": "FR76100000000000000000001"},
    {"id": 2, "name": "EDF", "iban": "FR76200000000000000000002"},
]

# --- Routes ---

@router.get("/", response_model=List[BeneficiaryResponse])
def get_beneficiaries():
    return fake_beneficiaries_db

@router.post("/", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary: BeneficiaryCreate):
    new_id = 1
    if fake_beneficiaries_db:
        new_id = max(b["id"] for b in fake_beneficiaries_db) + 1
    
    new_entry = beneficiary.dict()
    new_entry["id"] = new_id
    
    fake_beneficiaries_db.append(new_entry)
    return new_entry

@router.patch("/{id}/", response_model=BeneficiaryResponse)
def update_beneficiary(id: int, beneficiary_update: BeneficiaryUpdate):
    current_beneficiary = next((b for b in fake_beneficiaries_db if b["id"] == id), None)
    
    if not current_beneficiary:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    
    update_data = beneficiary_update.dict(exclude_unset=True)
    current_beneficiary.update(update_data)
    
    return current_beneficiary

@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(id: int):
    global fake_beneficiaries_db
    initial_length = len(fake_beneficiaries_db)
    fake_beneficiaries_db = [b for b in fake_beneficiaries_db if b["id"] != id]
    
    if len(fake_beneficiaries_db) == initial_length:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    
    return None