# Fichier: app/models/beneficiary.py

from pydantic import BaseModel
from typing import Optional

# --- Définition des Modèles (Schemas) ---

class BeneficiaryBase(BaseModel):
    name: str
    iban: str

class BeneficiaryCreate(BeneficiaryBase):
    """Schéma pour la création (POST)"""
    pass

class BeneficiaryUpdate(BaseModel):
    """Schéma pour la mise à jour (PATCH) - tout est optionnel"""
    name: Optional[str] = None
    iban: Optional[str] = None

class BeneficiaryResponse(BeneficiaryBase):
    """Schéma pour la réponse (GET) - inclut l'ID"""
    id: int