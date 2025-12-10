from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_status_code():
    """Vérifie que la page d'accueil répond bien (code 200)"""
    response = client.get("/")
    assert response.status_code == 200