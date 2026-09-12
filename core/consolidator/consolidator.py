import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from core.models import Event, Memory, ConsolidationLog, Persona, User
from core.adapters.anthropic_adapter import AnthropicProvider

logger = logging.getLogger(__name__)

class BeliefConsolidator:
    def __init__(self, db: Session, llm_provider: AnthropicProvider = None):
        self.db = db
        self.llm = llm_provider or AnthropicProvider()

    async def consolidate_user(self, user_id: UUID) -> Dict[str, Any]:
        """Ejecutar ciclo completo de consolidación para un usuario"""
        logger.info(f"Iniciando consolidación para usuario {user_id}")

        events = self._get_unconsolidated_events(user_id)
        if not events:
            logger.info(f"Sin eventos nuevos para consolidar para {user_id}")
            return {"consolidated_events": 0, "new_memories": 0}

        memories = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.status == "activa"
        ).all()

        consolidation_result = await self.llm.consolidate_beliefs(
            events=[self._event_to_dict(e) for e in events],
            existing_memories=[self._memory_to_dict(m) for m in memories]
        )

        # Procesar nuevas creencias
        new_memories_count = 0
        for new_belief in consolidation_result.get("new_memories", []):
            memory = Memory(
                user_id=user_id,
                belief=new_belief["creencia"],
                category=new_belief["categoria"],
                confidence=new_belief.get("confidence", 0.3),
                status="activa",
                origin_event_ids=[e.id for e in events[:3]]
            )
            self.db.add(memory)
            self.db.flush()

            self._log_consolidation(
                user_id=user_id,
                event_id=None,
                decision="NEW_PATTERN",
                memory_id=memory.id,
                reasoning=new_belief["creencia"]
            )
            new_memories_count += 1

        # Procesar confirmaciones
        for confirmation in consolidation_result.get("confirmations", []):
            memory_id = confirmation["memory_id"]
            new_confidence = confirmation["new_confidence"]

            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                memory.last_confirmed = datetime.utcnow()
                memory.confidence = min(new_confidence, 0.95)

                self._log_consolidation(
                    user_id=user_id,
                    event_id=None,
                    decision="CONFIRMS",
                    memory_id=memory_id,
                    reasoning=f"Confianza actualizada a {new_confidence}"
                )

        # Procesar contradicciones
        contradictions_count = 0
        for contradiction in consolidation_result.get("contradictions", []):
            old_memory_id = contradiction["memory_id"]
            old_memory = self.db.query(Memory).filter(Memory.id == old_memory_id).first()

            if old_memory:
                old_memory.status = "refutada"

                new_memory = Memory(
                    user_id=user_id,
                    belief=old_memory.belief + f" [REFUTADA: {contradiction.get('reason', 'contradictorio')}]",
                    category=old_memory.category,
                    confidence=0.0,
                    status="refutada",
                )
                self.db.add(new_memory)
                self.db.flush()

                self._log_consolidation(
                    user_id=user_id,
                    event_id=None,
                    decision="CONTRADICTS",
                    memory_id=new_memory.id,
                    memory_old_id=old_memory_id,
                    reasoning=contradiction.get("reason")
                )
                contradictions_count += 1

        # Aplicar decaimiento
        self._apply_decay(user_id)

        self.db.commit()

        logger.info(f"Consolidación completada: {len(events)} eventos, {new_memories_count} nuevas creencias")

        return {
            "consolidated_events": len(events),
            "new_memories": new_memories_count,
            "contradictions": contradictions_count
        }

    async def version_persona(self, user_id: UUID) -> Dict[str, Any]:
        """Crear nueva versión de persona trimestral"""
        logger.info(f"Versionando persona para {user_id}")

        current_persona = self.db.query(Persona).filter(
            Persona.user_id == user_id,
            Persona.is_active == True
        ).order_by(Persona.version.desc()).first()

        memories = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.status == "activa"
        ).all()

        beliefs_text = "\n".join([f"- {m.belief}" for m in memories[:20]])

        prompt = f"""Basándote en estas creencias sobre una persona, resume quién es en máx 300 palabras:

{beliefs_text}

Proporciona un JSON con:
{{
  "summary": "resumen en 300 palabras",
  "values": ["valor1", "valor2", ...],
  "patterns": ["patrón1", "patrón2", ...],
  "contradictions": ["contradicción1", ...]
}}
"""

        response_text = await self.llm.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="Eres un analista de personalidad. Genera perfiles basados en creencias reales."
        )

        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            persona_data = json.loads(response_text[start_idx:end_idx])
        except:
            persona_data = {
                "summary": f"Versión {(current_persona.version if current_persona else 0) + 1}",
                "values": [],
                "patterns": [],
                "contradictions": []
            }

        new_persona = Persona(
            user_id=user_id,
            version=(current_persona.version + 1) if current_persona else 1,
            temporal_range_start=datetime.utcnow(),
            summary=persona_data.get("summary"),
            values=persona_data.get("values", []),
            patterns=persona_data.get("patterns", []),
            contradictions=persona_data.get("contradictions", []),
            parent_id=current_persona.id if current_persona else None
        )

        # Extraer muestras de voz
        events = self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.consent_revoked == False
        ).order_by(Event.timestamp.desc()).limit(50).all()

        voice_samples = await self.llm.extract_voice_samples(
            [e.content for e in events]
        )
        new_persona.voice_samples = voice_samples

        if current_persona:
            current_persona.is_active = False

        self.db.add(new_persona)
        self.db.commit()

        logger.info(f"Persona versionada: v{new_persona.version}")
        return {"version": new_persona.version, "summary": new_persona.summary}

    def _get_unconsolidated_events(self, user_id: UUID, days_back: int = 7) -> List[Event]:
        """Obtener eventos no consolidados de los últimos N días"""
        cutoff = datetime.utcnow() - timedelta(days=days_back)

        events = self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.timestamp >= cutoff,
            Event.consent_revoked == False
        ).order_by(Event.timestamp.asc()).all()

        return events

    def _apply_decay(self, user_id: UUID):
        """Aplicar decaimiento a memorias no confirmadas recientemente"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        decayed_memories = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.status == "activa",
            Memory.last_confirmed < thirty_days_ago,
            Memory.emotional_weight < 0.7  # Proteger emocionales
        ).all()

        for memory in decayed_memories:
            memory.confidence *= 0.9
            if memory.confidence < 0.1:
                memory.status = "decaida"

    def _event_to_dict(self, event: Event) -> Dict[str, Any]:
        return {
            "id": str(event.id),
            "timestamp": event.timestamp.isoformat(),
            "type": event.event_type.value,
            "content": event.content,
            "context": event.context,
            "emotional_weight": event.emotional_weight
        }

    def _memory_to_dict(self, memory: Memory) -> Dict[str, Any]:
        return {
            "id": str(memory.id),
            "belief": memory.belief,
            "category": memory.category,
            "confidence": memory.confidence,
            "status": memory.status
        }

    def _log_consolidation(
        self,
        user_id: UUID,
        event_id: UUID = None,
        decision: str = "",
        memory_id: UUID = None,
        memory_old_id: UUID = None,
        reasoning: str = None
    ):
        log = ConsolidationLog(
            user_id=user_id,
            event_id=event_id,
            decision=decision,
            memory_id=memory_id,
            memory_old_id=memory_old_id,
            llm_model="claude-3-5-sonnet",
            prompt_version="v1.0",
            reasoning=reasoning
        )
        self.db.add(log)
