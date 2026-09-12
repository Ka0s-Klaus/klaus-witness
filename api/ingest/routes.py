from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from core.database import get_db
from core.models import Event, User
from core.models import EventType, ConsentLevel
from core.schemas.event_schemas import EventCreateSchema, EventResponseSchema, EventListSchema
from api.auth.security import get_current_user

router = APIRouter()

@router.post("/", response_model=EventResponseSchema)
async def create_event(
    event_data: EventCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo evento"""
    event = Event(
        user_id=current_user.id,
        event_type=EventType(event_data.tipo),
        content=event_data.contenido,
        context=event_data.contexto.dict(),
        emotional_weight=event_data.peso_emocional,
        consent_level=ConsentLevel(event_data.consentimiento.nivel),
        consent_granted_at=event_data.consentimiento.otorgado_en,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event

@router.get("/", response_model=EventListSchema)
async def list_events(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar eventos del usuario"""
    query = db.query(Event).filter(Event.user_id == current_user.id)
    total = query.count()

    events = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit).all()

    return EventListSchema(
        total=total,
        events=events,
        has_more=(skip + limit) < total
    )

@router.get("/{event_id}", response_model=EventResponseSchema)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener un evento específico"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    return event

@router.delete("/{event_id}", status_code=204)
async def revoke_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revocar consentimiento de un evento (no borra, solo marca)"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    event.consent_revoked = True
    event.consent_revoked_at = datetime.utcnow()

    db.commit()
    return None
