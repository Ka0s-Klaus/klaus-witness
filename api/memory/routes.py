from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel

from core.database import get_db
from core.models import Memory, User
from api.auth.security import get_current_user

router = APIRouter()

class MemoryResponseSchema(BaseModel):
    id: UUID
    belief: str
    category: str
    confidence: float
    status: str
    first_seen: str
    last_confirmed: str

    class Config:
        from_attributes = True

class MemoryListSchema(BaseModel):
    memories: List[MemoryResponseSchema]
    total: int

@router.get("/", response_model=MemoryListSchema)
async def list_memories(
    category: str = None,
    status: str = "activa",
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar memorias semánticas del usuario"""
    query = db.query(Memory).filter(
        Memory.user_id == current_user.id,
        Memory.status == status
    )

    if category:
        query = query.filter(Memory.category == category)

    total = query.count()
    memories = query.order_by(Memory.last_confirmed.desc()).offset(skip).limit(limit).all()

    return MemoryListSchema(
        memories=memories,
        total=total
    )

@router.get("/{memory_id}", response_model=MemoryResponseSchema)
async def get_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener una memoria específica"""
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()

    if not memory:
        raise HTTPException(status_code=404, detail="Memoria no encontrada")

    return memory

@router.get("/search")
async def search_memories(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Buscar memorias por texto (BM25 simple)"""
    memories = db.query(Memory).filter(
        Memory.user_id == current_user.id,
        Memory.status == "activa",
        Memory.belief.ilike(f"%{q}%")
    ).order_by(Memory.confidence.desc()).limit(10).all()

    return {"memories": memories, "total": len(memories)}
