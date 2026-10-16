import json
from typing import List, Dict, Any
from app.core.redis import redis_client


class MemoryService:
    """Manages fast short-term message buffer in Redis for prompt context window assembly."""

    @staticmethod
    def _get_key(thread_id: str) -> str:
        return f"thread:{thread_id}:memory"

    def push_message(self, thread_id: str, sender: str, content: str) -> None:
        """Pushes a user or assistant message to Redis memory (TTL 24 hours)."""
        if not redis_client:
            return
        
        key = self._get_key(thread_id)
        msg_payload = json.dumps({"sender": sender, "content": content})
        
        try:
            redis_client.rpush(key, msg_payload)
            redis_client.expire(key, 86400)  # 24 hour expiration
        except Exception:
            pass  # Fallback gracefully if Redis is unavailable

    def get_recent_messages(self, thread_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieves the last N messages for context prompt injection."""
        if not redis_client:
            return []
        
        key = self._get_key(thread_id)
        try:
            raw_items = redis_client.lrange(key, -limit, -1)
            return [json.loads(item) for item in raw_items]
        except Exception:
            return []

    def clear_thread_memory(self, thread_id: str) -> None:
        """Flushes short-term memory buffer when a thread is deleted or reset."""
        if not redis_client:
            return
        key = self._get_key(thread_id)
        try:
            redis_client.delete(key)
        except Exception:
            pass


memory_service = MemoryService()