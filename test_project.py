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

def test_create_and_delete_campaign_integration():
    """
    Prueba de integración que verifica la creación y posterior eliminación
    de una misma campaña.
    """
    # 1. Crear una nueva campaña para la prueba
    create_response = client.post(
        "/campaings",
        json={"name": "Campaña a Eliminar", "due_date": "2025-11-20T10:00:00"},
    )
    assert create_response.status_code == 201, f"Fallo al crear la campaña: {create_response.text}"
    created_data = create_response.json().get("data", {})
    campaing_id_to_delete = created_data.get("campaing_id")
    assert campaing_id_to_delete is not None

    # 2. Eliminar la campaña recién creada usando su ID
    delete_response = client.delete(f"/campaings/{campaing_id_to_delete}")
    
    # Suponiendo que el endpoint de eliminación devuelve un 200 OK con un mensaje
    assert delete_response.status_code == 204, f"Se esperaba 204 pero se recibió {delete_response.status_code}"
    assert not delete_response.content

    # 3. Verificar que la campaña ya no existe
    # Al intentar obtener la campaña eliminada, esperamos un error 404
    get_response = client.get(f"/campaings/{campaing_id_to_delete}")
    assert get_response.status_code == 404, f"La campaña con ID {campaing_id_to_delete} no fue eliminada correctamente."
