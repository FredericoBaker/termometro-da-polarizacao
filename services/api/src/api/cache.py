import hashlib
import json
import os
from datetime import date, datetime
from typing import Any, Callable

import redis


DEFAULT_TTL_SECONDS = 60 * 60 * 24  # 1 day


class ApiCache:
    def __init__(
        self,
        redis_url: str | None = None,
        key_prefix: str = "termopol-api",
        default_ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        self.key_prefix = key_prefix
        self.default_ttl_seconds = default_ttl_seconds
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.Redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_timeout=1,
            socket_connect_timeout=1,
        )

    def _is_bypass_enabled(self) -> bool:
        bypass = os.getenv("CACHE_BYPASS", "").strip().lower()
        return bypass in {"1", "true", "yes", "on"}

    @staticmethod
    def _normalize(value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: ApiCache._normalize(v) for k, v in sorted(value.items())}
        if isinstance(value, list):
            return [ApiCache._normalize(v) for v in value]
        if isinstance(value, tuple):
            return [ApiCache._normalize(v) for v in value]
        return value

    def make_key(self, namespace: str, **kwargs: Any) -> str:
        payload = self._normalize(kwargs)
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        hashed = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{self.key_prefix}:{namespace}:{hashed}"

    def get(self, key: str) -> Any | None:
        if self._is_bypass_enabled():
            return None
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        if self._is_bypass_enabled():
            return
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        try:
            serialized = json.dumps(value, ensure_ascii=True, default=str)
            self.client.setex(key, ttl, serialized)
        except Exception:
            return

    def get_or_set(
        self,
        key: str,
        producer: Callable[[], Any],
        ttl_seconds: int | None = None,
    ) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached

        value = producer()
        self.set(key, value, ttl_seconds=ttl_seconds)
        return value
