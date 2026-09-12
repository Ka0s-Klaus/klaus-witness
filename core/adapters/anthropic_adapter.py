from .base import LLMProvider
from anthropic import Anthropic
from config import settings
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model

    async def generate_embedding(self, text: str) -> List[float]:
        # Para v1.0, usamos embeddings simples basados en hash + texto
        # En v1.1 se reemplaza con embeddings reales de Anthropic/OpenAI
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = [float(b) / 256.0 for b in hash_bytes[:64]]
        return embedding

    async def chat_completion(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        try:
            full_messages = messages.copy()
            if system_prompt:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=system_prompt,
                    messages=full_messages
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    messages=full_messages
                )

            return response.content[0].text
        except Exception as e:
            logger.error(f"Error in chat_completion: {e}")
            raise

    async def consolidate_beliefs(self, events: List[Dict], existing_memories: List[Dict]) -> Dict[str, Any]:
        prompt = f"""
Analiza estos eventos de una persona y consolida creencias sobre ella.

EVENTOS RECIENTES:
{json.dumps(events, ensure_ascii=False, indent=2)}

CREENCIAS EXISTENTES:
{json.dumps(existing_memories, ensure_ascii=False, indent=2)}

Responde en JSON con estructura:
{{
  "new_memories": [
    {{"creencia": "texto", "categoria": "valor|patron|relacion|objetivo|temor|habito", "confidence": 0.0-1.0}}
  ],
  "confirmations": [
    {{"memory_id": "uuid", "new_confidence": 0.0-1.0}}
  ],
  "contradictions": [
    {{"memory_id": "uuid", "reason": "explicación"}}
  ]
}}
"""
        response_text = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="Eres un consolidador de memoria personal. Analiza eventos y genera creencias estructuradas."
        )

        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing consolidation response: {e}")

        return {"new_memories": [], "confirmations": [], "contradictions": []}

    async def extract_voice_samples(self, texts: List[str]) -> List[str]:
        if not texts:
            return []

        prompt = f"""
De estos textos, extrae 3-5 fragmentos que representen mejor la voz y personalidad de la persona:

{json.dumps(texts, ensure_ascii=False)}

Responde SOLO con un JSON array de strings (los fragmentos):
["fragmento 1", "fragmento 2", ...]
"""
        response_text = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="Extrae fragmentos característicos que muestren la voz única de una persona."
        )

        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing voice samples: {e}")

        return texts[:3]

    async def generate_future_scenario(self, persona: Dict, scenario_type: str = "tendencial") -> str:
        prompt = f"""
Basado en esta persona y sus patrones, genera un escenario futuro.

PERSONA:
{json.dumps(persona, ensure_ascii=False, indent=2)}

TIPO DE ESCENARIO: {scenario_type}
- tendencial: continuación natural de su camino actual
- optimista: mejor versión posible
- arrepentimiento: reflexión sobre decisiones no tomadas

Escribe como si fuera un monólogo del yo futuro de esta persona. Máximo 500 palabras.
"""
        response = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="Eres un espejo narrativo del futuro de alguien. Escribes con su voz, basado en sus valores y patrones reales."
        )

        return response
