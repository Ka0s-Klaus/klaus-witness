from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json

class MemoryStore(ABC):
    @abstractmethod
    async def get_memories(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def create_memory(self, user_id: str, belief: str, category: str, confidence: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_memory_confidence(self, memory_id: str, confidence: float) -> None:
        pass

class LLMProvider(ABC):
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        pass

    @abstractmethod
    async def consolidate_beliefs(self, events: List[Dict], existing_memories: List[Dict]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def extract_voice_samples(self, texts: List[str]) -> List[str]:
        pass

    @abstractmethod
    async def generate_future_scenario(self, persona: Dict, scenario_type: str) -> str:
        pass
