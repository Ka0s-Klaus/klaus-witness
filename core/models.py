from sqlalchemy import Column, String, DateTime, Float, Integer, Text, JSON, Boolean, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid
import enum

class EventType(str, enum.Enum):
    DECISION = "decision"
    EMOTION = "emotion"
    FACT = "fact"
    REFLECTION = "reflection"
    CONVERSATION = "conversation"
    VITAL_MILESTONE = "hito_vital"

class ConsentLevel(str, enum.Enum):
    PERSONAL = "personal"
    FAMILY = "familiar"
    LEGACY = "legado"

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(JSONB, default={})
    emotional_weight = Column(Float, default=0.0)

    consent_level = Column(Enum(ConsentLevel), default=ConsentLevel.PERSONAL)
    consent_granted_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    consent_revoked = Column(Boolean, default=False)
    consent_revoked_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    memories = relationship("Memory", back_populates="origin_events", secondary="event_memory_link")

    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_user_type', 'user_id', 'event_type'),
    )

class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    belief = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # valor, patron, relacion, objetivo, temor, habito
    first_seen = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_confirmed = Column(DateTime(timezone=True), default=datetime.utcnow)
    confidence = Column(Float, default=0.3)
    status = Column(String(20), default="activa")  # activa, decaida, refutada
    version = Column(Integer, default=1)

    embedding = Column(JSONB, nullable=True)  # Regenerable, not primary
    origin_event_ids = Column(JSON, default=[])

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    origin_events = relationship("Event", back_populates="memories", secondary="event_memory_link")

    __table_args__ = (
        Index('idx_user_belief', 'user_id', 'belief'),
        Index('idx_user_category', 'user_id', 'category'),
    )

class EventMemoryLink(Base):
    __tablename__ = "event_memory_link"

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), primary_key=True)
    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id"), primary_key=True)

class Persona(Base):
    __tablename__ = "personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    version = Column(Integer, default=1)

    temporal_range_start = Column(DateTime(timezone=True), nullable=False)
    temporal_range_end = Column(DateTime(timezone=True), nullable=True)

    summary = Column(Text, nullable=False)
    values = Column(JSON, default=[])
    patterns = Column(JSON, default=[])
    contradictions = Column(JSON, default=[])
    voice_samples = Column(JSON, default=[])

    parent_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=True)
    persona_type = Column(String(20), default="principal")  # principal, fork
    fork_description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_version', 'user_id', 'version'),
    )

class ConsolidationLog(Base):
    __tablename__ = "consolidation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)

    decision = Column(String(100), nullable=False)  # CONFIRMS, CONTRADICTS, NEW_PATTERN
    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id"), nullable=True)
    memory_old_id = Column(UUID(as_uuid=True), nullable=True)

    llm_model = Column(String(100), nullable=False)
    prompt_version = Column(String(50), nullable=False)
    reasoning = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_decision', 'user_id', 'decision'),
    )

class Extension(Base):
    __tablename__ = "extensions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    proposed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    motivation = Column(Text, nullable=False)
    code_path = Column(String(255), nullable=True)

    status = Column(String(50), default="proposed")  # proposed, approved, active, retired
    approved_by = Column(String(255), nullable=True)

    test_path = Column(String(255), nullable=True)
    audit_result = Column(JSON, default={})

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
    )

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))

    first_name = Column(String(100))
    last_name = Column(String(100))

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)
