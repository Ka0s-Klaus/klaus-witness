from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import json

from core.database import get_db
from core.models import User, Persona
from core.adapters.anthropic_adapter import AnthropicProvider
from api.auth.security import get_current_user
from .retrieval import hybrid_memory_retrieval
from .conversation import ConversationManager

router = APIRouter()

class MessageSchema(BaseModel):
    content: str

class ConversationResponseSchema(BaseModel):
    response: str
    citations: dict
    memory_sources: List[dict]

@router.post("/chat", response_model=ConversationResponseSchema)
async def chat(
    message: MessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conversar con el yo persona basado en memoria"""

    # Recuperar memorias relevantes
    memories = await hybrid_memory_retrieval(
        db=db,
        user_id=current_user.id,
        query=message.content,
        top_k=5,
        diversify_temporal=True
    )

    # Obtener persona activa
    persona = db.query(Persona).filter(
        Persona.user_id == current_user.id,
        Persona.is_active == True
    ).order_by(Persona.version.desc()).first()

    persona_dict = None
    if persona:
        persona_dict = {
            "version": persona.version,
            "values": persona.values,
            "voice_samples": persona.voice_samples,
            "summary": persona.summary
        }

    # Generar respuesta
    conversation_manager = ConversationManager(llm_provider=AnthropicProvider())
    result = await conversation_manager.chat_with_memory(
        user_query=message.content,
        retrieved_memories=memories,
        persona=persona_dict
    )

    return result

@router.post("/chat-stream")
async def chat_stream(
    message: MessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conversar con streaming (para UX en tiempo real)"""

    memories = await hybrid_memory_retrieval(
        db=db,
        user_id=current_user.id,
        query=message.content,
        top_k=5,
        diversify_temporal=True
    )

    persona = db.query(Persona).filter(
        Persona.user_id == current_user.id,
        Persona.is_active == True
    ).order_by(Persona.version.desc()).first()

    persona_dict = None
    if persona:
        persona_dict = {
            "values": persona.values,
            "voice_samples": persona.voice_samples,
        }

    async def generate():
        conversation_manager = ConversationManager(llm_provider=AnthropicProvider())
        result = await conversation_manager.chat_with_memory(
            user_query=message.content,
            retrieved_memories=memories,
            persona=persona_dict
        )

        yield json.dumps({
            "response": result["response"],
            "citations": result["citations"]
        }).encode() + b"\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
