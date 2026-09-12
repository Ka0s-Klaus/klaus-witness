from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from core.database import get_db
from core.models import User, Persona
from core.adapters.anthropic_adapter import AnthropicProvider
from api.auth.security import get_current_user

router = APIRouter()

class PersonaResponseSchema(BaseModel):
    id: UUID
    version: int
    summary: str
    values: List[str]
    patterns: List[str]
    voice_samples: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class FutureScenarioSchema(BaseModel):
    scenario_type: str = "tendencial"  # tendencial, optimista, arrepentimiento

@router.get("/current", response_model=PersonaResponseSchema)
async def get_current_persona(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener persona actual activa"""
    persona = db.query(Persona).filter(
        Persona.user_id == current_user.id,
        Persona.is_active == True
    ).order_by(Persona.version.desc()).first()

    if not persona:
        raise HTTPException(status_code=404, detail="No hay persona creada. Completa entrevistas primero.")

    return persona

@router.get("/versions", response_model=List[PersonaResponseSchema])
async def list_persona_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todas las versiones de la persona"""
    personas = db.query(Persona).filter(
        Persona.user_id == current_user.id
    ).order_by(Persona.version.desc()).all()

    return personas

@router.post("/future-self")
async def chat_with_future_self(
    scenario: FutureScenarioSchema,
    years_ahead: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conversar con tu yo futuro basado en extrapolación"""

    persona = db.query(Persona).filter(
        Persona.user_id == current_user.id,
        Persona.is_active == True
    ).order_by(Persona.version.desc()).first()

    if not persona:
        raise HTTPException(status_code=404, detail="No hay persona para proyectar")

    persona_dict = {
        "version": persona.version,
        "summary": persona.summary,
        "values": persona.values,
        "patterns": persona.patterns,
        "voice_samples": persona.voice_samples,
        "years_ahead": years_ahead
    }

    llm = AnthropicProvider()
    future_monologue = await llm.generate_future_scenario(
        persona=persona_dict,
        scenario_type=scenario.scenario_type
    )

    return {
        "monologue": future_monologue,
        "scenario_type": scenario.scenario_type,
        "years_ahead": years_ahead,
        "persona_version": persona.version
    }

@router.post("/{persona_id}/fork")
async def create_fork(
    persona_id: UUID,
    fork_description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear bifurcación de persona para explorar escenarios alternativos"""

    original = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.user_id == current_user.id
    ).first()

    if not original:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    fork = Persona(
        user_id=current_user.id,
        version=original.version,
        temporal_range_start=original.temporal_range_start,
        temporal_range_end=None,
        summary=original.summary,
        values=original.values,
        patterns=original.patterns,
        voice_samples=original.voice_samples,
        parent_id=original.id,
        persona_type="fork",
        fork_description=fork_description,
        is_active=False
    )

    db.add(fork)
    db.commit()
    db.refresh(fork)

    return {
        "fork_id": str(fork.id),
        "fork_description": fork_description,
        "parent_version": original.version
    }
