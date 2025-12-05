from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserDB


def get_current_user_from_session(request: Request, db: Session = Depends(get_db)) -> UserDB:
    """
    Récupère l'utilisateur connecté depuis la session.
    Lève une exception si l'utilisateur n'est pas connecté.
    
    Cette fonction peut être utilisée comme dépendance FastAPI dans les endpoints.
    """
    user_email = None
    if hasattr(request, "session"):
        user_email = request.session.get("user_email")
    
    if not user_email:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return user


def get_user_email_from_session(request: Request) -> str | None:
    """
    Récupère l'email de l'utilisateur depuis la session sans interroger la base de données.
    Retourne None si l'utilisateur n'est pas connecté.
    
    Utile pour les routes web qui veulent simplement vérifier la présence d'une session.
    """
    if hasattr(request, "session"):
        return request.session.get("user_email")
    return None
