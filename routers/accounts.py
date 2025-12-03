from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/accounts",tags=["Comptes"])
templates = Jinja2Templates(directory="templates")

fake_db_accounts = {
    1: {"owner": "test", "type": "Courant", "transactions": [100, -50, -20, 500]},
    2: {"owner": "test", "type": "Livret A", "transactions": [5000, 100]},
    3: {"owner": "Elon Musk", "type": "Courant", "transactions": [999999, -1]},
}

@router.get("/{account_id}")
async def get_account_balance(request: Request, account_id: int):
    account_data = fake_db_accounts.get(account_id)
    if not account_data :
        raise HTTPException(status_code=404, detail="Compte non trouvé")

    balance = sum(account_data["transactions"])

    return templates.TemplateResponse(
        request = request,
        name="pages/soldes.html",
        context={
            "id": account_id,
            "owner": account_data["owner"],
            "type": account_data["type"],
            "transactions": account_data["transactions"]
        }
    )




