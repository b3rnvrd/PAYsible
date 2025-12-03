# app/api/routers.py

from fastapi import APIRouter
from app.api.endpoints import users

router = APIRouter()

# Les routeurs spécifiques (users.py, accounts.py) seront inclus ici plus tard.
router.include_router(users.router)