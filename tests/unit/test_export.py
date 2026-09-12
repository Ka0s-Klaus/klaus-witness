import pytest
import json

def test_export_summary(client, test_user):
    """Obtener resumen de datos exportables"""
    token = json.dumps({"user_id": str(test_user.id)})

    response = client.get(
        "/api/export/summary",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "total_memories" in data
    assert "total_personas" in data
    assert data["user"]["id"] == str(test_user.id)

def test_export_download(client, test_user):
    """Descargar datos en formato JSON legible"""
    token = json.dumps({"user_id": str(test_user.id)})

    response = client.get(
        "/api/export/download",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "data" in response.json()
    assert "filename" in response.json()

    # Verificar que el JSON es legible y válido
    export_data = json.loads(response.json()["data"])
    assert "metadata" in export_data
    assert "data" in export_data
    assert "statistics" in export_data
    assert export_data["metadata"]["user_id"] == str(test_user.id)

def test_export_format_structure(client, test_user):
    """Verificar estructura del export JSON"""
    token = json.dumps({"user_id": str(test_user.id)})

    response = client.get(
        "/api/export/download",
        headers={"Authorization": f"Bearer {token}"}
    )

    export_data = json.loads(response.json()["data"])

    # Campos obligatorios
    assert "format_version" in export_data["metadata"]
    assert "license" in export_data["metadata"]
    assert "events" in export_data["data"]
    assert "memories" in export_data["data"]
    assert "personas" in export_data["data"]

def test_export_without_auth(client):
    """Export requiere autenticación"""
    response = client.get("/api/export/summary")
    assert response.status_code in [401, 403]
