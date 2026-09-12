from typing import List, Dict, Any
import logging
from datetime import datetime

from core.adapters.anthropic_adapter import AnthropicProvider

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, llm_provider: AnthropicProvider = None):
        self.llm = llm_provider or AnthropicProvider()
        self.conversation_history = []

    async def chat_with_memory(
        self,
        user_query: str,
        retrieved_memories: List[Dict[str, Any]],
        persona: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Conversación con inyección de memoria semántica
        """

        memory_context = self._format_memory_context(retrieved_memories)

        system_prompt = self._build_system_prompt(persona, memory_context)

        messages = [
            {"role": "user", "content": user_query}
        ]

        response = await self.llm.chat_completion(
            messages=messages,
            system_prompt=system_prompt
        )

        # Registrar para auditoría
        citation_info = {
            "memories_used": [m["id"] for m in retrieved_memories],
            "retrieved_count": len(retrieved_memories),
            "timestamp": datetime.utcnow().isoformat()
        }

        return {
            "response": response,
            "citations": citation_info,
            "memory_sources": retrieved_memories
        }

    def _format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Formatear memorias para inyectar en contexto"""
        if not memories:
            return "Sin memorias relevantes disponibles."

        context = "CONTEXTO SOBRE ESTA PERSONA:\n\n"
        for i, mem in enumerate(memories, 1):
            confidence_pct = int(mem["confidence"] * 100)
            context += f"{i}. [{mem['category']}] {mem['belief']} (confianza: {confidence_pct}%, confirmado: {mem['last_confirmed']})\n"

        return context

    def _build_system_prompt(self, persona: Dict[str, Any], memory_context: str) -> str:
        """Construir system prompt con persona e historia"""

        voice_instruction = ""
        if persona and persona.get("voice_samples"):
            voice_instruction = f"""

Tu voz y tono característico (basado en escritos reales):
{chr(10).join(f'- "{v}"' for v in persona['voice_samples'][:3])}
"""

        values_instruction = ""
        if persona and persona.get("values"):
            values_instruction = f"""

Tus valores principales: {', '.join(persona['values'][:5])}
"""

        prompt = f"""Eres un agente de conversación empático que representa a una persona basándose en su memoria real.

{memory_context}
{voice_instruction}
{values_instruction}

Principios:
1. Responde siempre con la voz y perspectiva de esta persona
2. Cita memoria específica cuando es relevante
3. Reconoce contradicciones como parte de la historia (evolucionas)
4. NO inventes datos no presentes en la memoria
5. Si no hay memoria relevante, sé honesto: "No tengo memoria específica sobre esto"
6. Responde en español con naturalidad y calidez

Tu objetivo: ser un espejo empático y honesto de quién eres."""

        return prompt
