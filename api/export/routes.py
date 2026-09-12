from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
from datetime import datetime
from io import BytesIO

from core.database import get_db
from core.models import User, Event, Memory, Persona, ConsolidationLog
from api.auth.security import get_current_user

router = APIRouter()

@router.get("/download")
async def export_user_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exportar completamente los datos del usuario en JSON legible.
    Sin costes, sin fricción, derecho del usuario.
    """

    # Eventos
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    events_data = [
        {
            "id": str(e.id),
            "timestamp": e.timestamp.isoformat(),
            "type": e.event_type.value,
            "content": e.content,
            "context": e.context,
            "emotional_weight": e.emotional_weight,
            "consent_level": e.consent_level.value,
            "consent_revoked": e.consent_revoked,
            "created_at": e.created_at.isoformat()
        }
        for e in events
    ]

    # Memorias
    memories = db.query(Memory).filter(Memory.user_id == current_user.id).all()
    memories_data = [
        {
            "id": str(m.id),
            "belief": m.belief,
            "category": m.category,
            "confidence": m.confidence,
            "status": m.status,
            "first_seen": m.first_seen.isoformat(),
            "last_confirmed": m.last_confirmed.isoformat(),
            "version": m.version
        }
        for m in memories
    ]

    # Personas
    personas = db.query(Persona).filter(Persona.user_id == current_user.id).all()
    personas_data = [
        {
            "id": str(p.id),
            "version": p.version,
            "temporal_range_start": p.temporal_range_start.isoformat(),
            "temporal_range_end": p.temporal_range_end.isoformat() if p.temporal_range_end else None,
            "summary": p.summary,
            "values": p.values,
            "patterns": p.patterns,
            "contradictions": p.contradictions,
            "voice_samples": p.voice_samples,
            "persona_type": p.persona_type,
            "fork_description": p.fork_description,
            "created_at": p.created_at.isoformat()
        }
        for p in personas
    ]

    # Logs de consolidación
    logs = db.query(ConsolidationLog).filter(ConsolidationLog.user_id == current_user.id).all()
    logs_data = [
        {
            "decision": l.decision,
            "memory_id": str(l.memory_id) if l.memory_id else None,
            "llm_model": l.llm_model,
            "prompt_version": l.prompt_version,
            "reasoning": l.reasoning,
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]

    # Estructura final
    export_data = {
        "metadata": {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "format_version": "1.0",
            "license": "User owns all data - unrestricted right to export, import, or delete"
        },
        "data": {
            "events": events_data,
            "memories": memories_data,
            "personas": personas_data,
            "consolidation_logs": logs_data
        },
        "statistics": {
            "total_events": len(events_data),
            "total_memories": len(memories_data),
            "total_personas": len(personas_data),
            "consolidation_decisions": len(logs_data)
        }
    }

    # Retornar como JSON descargable
    json_data = json.dumps(export_data, ensure_ascii=False, indent=2)

    return {
        "data": json_data,
        "filename": f"testigo_export_{current_user.username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    }

@router.get("/summary")
async def export_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resumen rápido de datos sin descargar todo"""
    events_count = db.query(Event).filter(Event.user_id == current_user.id).count()
    memories_count = db.query(Memory).filter(Memory.user_id == current_user.id).count()
    personas_count = db.query(Persona).filter(Persona.user_id == current_user.id).count()

    first_event = db.query(Event).filter(
        Event.user_id == current_user.id
    ).order_by(Event.timestamp.asc()).first()

    last_event = db.query(Event).filter(
        Event.user_id == current_user.id
    ).order_by(desc(Event.timestamp)).first()

    return {
        "total_events": events_count,
        "total_memories": memories_count,
        "total_personas": personas_count,
        "data_span": {
            "first_event": first_event.timestamp.isoformat() if first_event else None,
            "last_event": last_event.timestamp.isoformat() if last_event else None
        },
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "created_at": current_user.created_at.isoformat()
        }
    }
