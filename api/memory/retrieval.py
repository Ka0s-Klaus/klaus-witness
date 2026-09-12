from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from core.models import Memory

async def hybrid_memory_retrieval(
    db: Session,
    user_id: UUID,
    query: str,
    top_k: int = 5,
    diversify_temporal: bool = True
) -> List[Dict[str, Any]]:
    """
    Recuperación híbrida: BM25 + diversidad temporal
    - Busca memorias relevantes
    - Selecciona top-k con prioridad en recencia confirmada
    - Diversifica temporalmente para evitar sesgo reciente
    """

    # BM25 simple: buscar coincidencias en creencias
    relevant = db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.status == "activa",
        Memory.belief.ilike(f"%{query}%")
    ).order_by(Memory.confidence.desc()).limit(top_k * 3).all()

    if not relevant:
        # Fallback: memorias más confiadas recientes
        relevant = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.status == "activa"
        ).order_by(Memory.confidence.desc()).limit(top_k).all()

    # Diversidad temporal: preferir spreads históricos
    if diversify_temporal and len(relevant) > 1:
        selected = []
        now = datetime.utcnow()
        time_buckets = [
            now - timedelta(days=7),
            now - timedelta(days=30),
            now - timedelta(days=90),
        ]

        for bucket_end in time_buckets:
            bucket_start = bucket_end - timedelta(days=20) if bucket_end != time_buckets[0] else datetime.min

            bucket_memories = [
                m for m in relevant
                if bucket_start <= m.last_confirmed <= bucket_end
            ]

            if bucket_memories:
                selected.append(max(bucket_memories, key=lambda m: m.confidence))

        # Completar con las mejores si es necesario
        selected_ids = {m.id for m in selected}
        for m in relevant:
            if m.id not in selected_ids and len(selected) < top_k:
                selected.append(m)

        relevant = selected[:top_k]

    return [
        {
            "id": str(m.id),
            "belief": m.belief,
            "category": m.category,
            "confidence": m.confidence,
            "last_confirmed": m.last_confirmed.isoformat(),
            "status": m.status
        }
        for m in relevant
    ]
