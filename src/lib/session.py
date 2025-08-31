import os
import redis.asyncio as redis
from fastapi import Request


class SessionDataService:
    _redis = None

    @classmethod
    async def initialize(cls, redis_url: str):
        """Initialize Redis connection"""
        cls._redis = redis.from_url(redis_url, decode_responses=True)

    @classmethod
    async def set_session_data(cls, request: Request, key: str, value: str, ttl_minutes: int = 60):
        """Set session data with expiry"""
        email_id = request.headers.get("soha-user")
        if not email_id:
            raise ValueError("Missing 'soha-user' header")

        cache_key = f"{email_id}:{key}"
        await cls._redis.set(cache_key, value, ex=ttl_minutes * 60)

    @classmethod
    async def get_session_data(cls, request: Request, key: str):
        """Get session data"""
        email_id = request.headers.get("soha-user")
        if not email_id:
            raise ValueError("Missing 'soha-user' header")

        cache_key = f"{email_id}:{key}"
        return await cls._redis.get(cache_key)