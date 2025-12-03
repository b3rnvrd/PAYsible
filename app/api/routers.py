# app/api/routers.py

from fastapi import APIRouter
from app.api.endpoints import beneficiaries

router = APIRouter()

# Les routeurs spécifiques (users.py, accounts.py) seront inclus ici plus tard.

router.include_router(
    beneficiaries.router, 
    prefix="/beneficiaries", 
    tags=["beneficiaries"]
)