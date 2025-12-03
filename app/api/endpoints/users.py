from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Schémas Pydantic
class UserResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

# Mock user pour la démo (à remplacer par une vraie base de données)
MOCK_USER = {
    "id": 1,
    "email": "demo@paysible.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+33 6 00 00 00 00",
    "address": "123 Rue de la Paix, 75000 Paris"
}


@router.get("/me/", response_model=UserResponse)
async def get_current_user():
    """
    Récupère les informations de l'utilisateur connecté (Profil).
    
    Endpoint: GET /api/users/me/
    """
    return MOCK_USER


@router.patch("/me/", response_model=UserResponse)
async def update_current_user(user_update: UserUpdate):
    """
    Modifie les informations de l'utilisateur connecté.
    
    Endpoint: PATCH /api/users/me/
    Payload: { "address": "...", "phone": "...", "first_name": "...", "last_name": "..." }
    """
    # Dans une vraie application, on mettrait à jour la base de données
    # Ici, on simule la mise à jour
    global MOCK_USER
    
    if user_update.first_name is not None:
        MOCK_USER["first_name"] = user_update.first_name
    if user_update.last_name is not None:
        MOCK_USER["last_name"] = user_update.last_name
    if user_update.phone is not None:
        MOCK_USER["phone"] = user_update.phone
    if user_update.address is not None:
        MOCK_USER["address"] = user_update.address
    
    return MOCK_USER
