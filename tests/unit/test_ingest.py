import pytest
from uuid import uuid4
import json
from core.models import Event, EventType, ConsentLevel
from datetime import datetime

def test_create_event(client, test_user, test_db):
    """Crear un evento válido"""
    token = json.dumps({"user_id": str(test_user.id)})

    response = client.post(
        "/api/events/",
        json={
            "tipo": "fact",
            "contenido": "Hoy aprendí algo nuevo sobre mí mismo.",
            "contexto": {"lugar": "casa", "etapa_vital": "reflexión"},
            "peso_emocional": 0.7,
            "consentimiento": {"nivel": "personal"}
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tipo"] == "fact"
    assert data["contenido"] == "Hoy aprendí algo nuevo sobre mí mismo."
    assert data["user_id"] == str(test_user.id)

def test_list_events(client, test_user, test_db):
    """Listar eventos del usuario"""
    token = json.dumps({"user_id": str(test_user.id)})

    # Crear múltiples eventos
    for i in range(3):
        client.post(
            "/api/events/",
            json={
                "tipo": "fact",
                "contenido": f"Evento {i+1}",
                "contexto": {},
                "peso_emocional": 0.5,
                "consentimiento": {"nivel": "personal"}
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    response = client.get(
        "/api/events/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3

def test_event_requires_auth(client):
    """Endpoint de eventos requiere autenticación"""
    response = client.post(
        "/api/events/",
        json={
            "tipo": "fact",
            "contenido": "test",
            "contexto": {},
            "peso_emocional": 0.5,
            "consentimiento": {"nivel": "personal"}
        }
    )

    assert response.status_code == 403 or response.status_code == 401

def test_event_content_validation(client, test_user):
    """Validar que contenido cumpla requisitos mínimos"""
    token = json.dumps({"user_id": str(test_user.id)})

    response = client.post(
        "/api/events/",
        json={
            "tipo": "fact",
            "contenido": "muy",  # < 10 caracteres
            "contexto": {},
            "peso_emocional": 0.5,
            "consentimiento": {"nivel": "personal"}
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422  # Validation error
