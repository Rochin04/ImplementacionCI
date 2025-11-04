import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session

from main import app, engine

TEST_DB_FILE = "database.db"
@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_database():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
        
    SQLModel.metadata.create_all(engine)

    yield
    os.remove(TEST_DB_FILE)

client = TestClient(app)
def test_create_campaign():
    """
    Prueba que el endpoint POST para crear una campaña funciona.
    """
    response = client.post(
        "/campaings", 
        json={"name": "Campaña de Prueba", "due_date": "2025-12-01T12:00:00"},
    )

    assert response.status_code == 201
    response_data = response.json()["data"]
    assert response_data["name"] == "Campaña de Prueba"
    assert "campaing_id" in response_data


def test_read_nonexistent_campaign():
    """
    Prueba que la API devuelve un 404 para una campaña que no existe.
    """
    response = client.get("/campaings/9999")
    assert response.status_code == 404