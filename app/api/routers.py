# app/api/routers.py

from fastapi import APIRouter
from app.api.endpoints import beneficiaries, users, accounts

router = APIRouter()

# Inclusion des routeurs spécifiques
router.include_router(users.router)
router.include_router(accounts.router)

router.include_router(
    beneficiaries.router, 
    prefix="/beneficiaries", 
    tags=["beneficiaries"]
)