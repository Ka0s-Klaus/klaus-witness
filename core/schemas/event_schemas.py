from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

class EventTypeEnum(str, Enum):
    DECISION = "decision"
    EMOTION = "emotion"
    FACT = "fact"
    REFLECTION = "reflection"
    CONVERSATION = "conversation"
    VITAL_MILESTONE = "hito_vital"

class ConsentLevelEnum(str, Enum):
    PERSONAL = "personal"
    FAMILY = "familiar"
    LEGACY = "legado"

class EventContextSchema(BaseModel):
    lugar: Optional[str] = None
    etapa_vital: Optional[str] = None
    personas: List[str] = []
    fuente: str = "app"

class ConsentSchema(BaseModel):
    nivel: ConsentLevelEnum = ConsentLevelEnum.PERSONAL
    otorgado_en: datetime = Field(default_factory=datetime.utcnow)
    revocable: bool = True

class EventCreateSchema(BaseModel):
    tipo: EventTypeEnum
    contenido: str = Field(..., min_length=10, max_length=5000)
    contexto: EventContextSchema = Field(default_factory=EventContextSchema)
    peso_emocional: float = Field(0.0, ge=0.0, le=1.0)
    consentimiento: ConsentSchema = Field(default_factory=ConsentSchema)

class EventResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    timestamp: datetime
    tipo: EventTypeEnum
    contenido: str
    contexto: Dict[str, Any]
    peso_emocional: float
    consentimiento: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class EventListSchema(BaseModel):
    total: int
    events: List[EventResponseSchema]
    has_more: bool = False
