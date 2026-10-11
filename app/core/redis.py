import json
import redis
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Initialize Redis connection pool
REDIS_HOST = getattr(settings, "REDIS_HOST", "localhost")
REDIS_PORT = getattr(settings, "REDIS_PORT", 6379)

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True
    )
except Exception as e:
    redis_client = None