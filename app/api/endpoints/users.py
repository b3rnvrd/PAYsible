from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.user import UserDB

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Schémas Pydantic
class UserResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None  # Mappé depuis 'name'
    last_name: Optional[str] = None
    phone: Optional[str] = None  # Mappé depuis 'phone_number'
    address: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@router.get("/me/", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    """
    Récupère les informations de l'utilisateur connecté (Profil).
    
    Endpoint: GET /api/users/me/
    """
    # Pour la démo, on prend le premier utilisateur
    # Dans une vraie app, on utiliserait l'ID de session ou un token JWT
    user = db.query(UserDB).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Mapper les champs de la DB vers le schéma de réponse
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.name,
        last_name=user.last_name,
        phone=user.phone_number,
        address=user.address
    )


@router.patch("/me/", response_model=UserResponse)
async def update_current_user(user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Modifie les informations de l'utilisateur connecté.
    
    Endpoint: PATCH /api/users/me/
    Payload: { "address": "...", "phone": "...", "first_name": "...", "last_name": "..." }
    """
    # Pour la démo, on prend le premier utilisateur
    user = db.query(UserDB).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Mettre à jour uniquement les champs fournis
    if user_update.first_name is not None:
        user.name = user_update.first_name
    if user_update.last_name is not None:
        user.last_name = user_update.last_name
    if user_update.phone is not None:
        user.phone_number = user_update.phone
    if user_update.address is not None:
        user.address = user_update.address
    
    db.commit()
    db.refresh(user)
    
    # Retourner le résultat avec les bons noms de champs
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.name,
        last_name=user.last_name,
        phone=user.phone_number,
        address=user.address
    )
