import asyncio
import json
import time
from typing import Any
import redis.asyncio as aioredis
from app.config import get_settings
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.services.waha import WAHAClient
from app.utils.db_session import async_session_factory
from app.utils.logger import get_logger

logger = get_logger("services.notification")
settings = get_settings()


class RateLimiter:
    """
    Rate Limiting / Throttling for interactive WhatsApp commands (/cek, /summary, /subscribe).
    Prevents spam commands and DDoS attacks. Uses Redis or falls back to in-memory window.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._memory_cache: dict[str, list[float]] = {}
        self._redis: aioredis.Redis | None = None
        self._lock = asyncio.Lock()

    async def _get_redis(self) -> aioredis.Redis | None:
        if self._redis is None:
            try:
                r = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
                await r.ping()
                self._redis = r
            except Exception:
                self._redis = None
        return self._redis

    async def is_rate_limited(self, phone_number: str) -> bool:
        r = await self._get_redis()
        now = time.time()
        key = f"rate_limit:{phone_number}"

        if r:
            try:
                count = await r.incr(key)
                if count == 1:
                    await r.expire(key, self.window_seconds)
                return count > self.max_requests
            except Exception:
                pass

        # In-memory fallback
        async with self._lock:
            timestamps = self._memory_cache.get(phone_number, [])
            timestamps = [t for t in timestamps if now - t < self.window_seconds]
            if len(timestamps) >= self.max_requests:
                return True
            timestamps.append(now)
            self._memory_cache[phone_number] = timestamps
            return False


class RedisCommandCache:
    """
    Redis Caching for aggregated interactive query results (/summary and /cek <TICKER>).
    TTL configured to 5-10 minutes (300-600 seconds) to reduce PostgreSQL query load.
    """

    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._memory_cache: dict[str, tuple[float, str]] = {}
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis | None:
        if self._redis is None:
            try:
                r = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
                await r.ping()
                self._redis = r
            except Exception:
                self._redis = None
        return self._redis

    async def get(self, key: str) -> str | None:
        r = await self._get_redis()
        if r:
            try:
                return await r.get(key)
            except Exception:
                pass
        entry = self._memory_cache.get(key)
        if entry:
            ts, val = entry
            if time.time() - ts < self.ttl_seconds:
                return val
            self._memory_cache.pop(key, None)
        return None

    async def set(self, key: str, value: str) -> None:
        r = await self._get_redis()
        if r:
            try:
                await r.set(key, value, ex=self.ttl_seconds)
                return
            except Exception:
                pass
        self._memory_cache[key] = (time.time(), value)


class NotificationCommandService:
    """
    Handles interactive WhatsApp slash commands: /cek <TICKER>, /summary, /subscribe <TICKER>, /unsubscribe <TICKER>.
    Includes Rate Limiter and Redis Caching.
    """

    def __init__(self):
        self.waha = WAHAClient()
        self.rate_limiter = RateLimiter(max_requests=15, window_seconds=60)
        self.cache = RedisCommandCache(ttl_seconds=300)  # 5 min TTL

    async def process_incoming_command(self, phone_number: str, text: str) -> str:
        """
        Parses incoming message from WAHA webhook, checks throttling, queries DB or cache, and returns response markdown.
        """
        cmd_clean = text.strip()

        # Check Rate Limiting / Throttling
        if await self.rate_limiter.is_rate_limited(phone_number):
            warn_msg = "⚠️ *Rate Limit Exceeded*: Anda telah mengirim terlalu banyak perintah. Silakan tunggu 1 menit."
            await self.waha.send_text(phone_number, warn_msg)
            return warn_msg

        if cmd_clean.lower().startswith("/cek"):
            parts = cmd_clean.split()
            if len(parts) < 2:
                resp = "⚠️ Format salah. Gunakan: `/cek <TICKER>` (contoh: `/cek BBCA` atau `/cek $BUMI`)."
                await self.waha.send_text(phone_number, resp)
                return resp
            ticker = parts[1].upper().lstrip("$")
            return await self._handle_cek_command(phone_number, ticker)

        if cmd_clean.lower() == "/summary":
            return await self._handle_summary_command(phone_number)

        if cmd_clean.lower().startswith("/subscribe"):
            parts = cmd_clean.split()
            if len(parts) < 2:
                resp = "⚠️ Format salah. Gunakan: `/subscribe <TICKER>` (contoh: `/subscribe BUMI`)."
                await self.waha.send_text(phone_number, resp)
                return resp
            ticker = parts[1].upper().lstrip("$")
            return await self._handle_subscribe_command(phone_number, ticker)

        if cmd_clean.lower().startswith("/unsubscribe"):
            parts = cmd_clean.split()
            if len(parts) < 2:
                resp = "⚠️ Format salah. Gunakan: `/unsubscribe <TICKER>` (contoh: `/unsubscribe BBCA`)."
                await self.waha.send_text(phone_number, resp)
                return resp
            ticker = parts[1].upper().lstrip("$")
            return await self._handle_unsubscribe_command(phone_number, ticker)

        # Ignore unrecognized non-command messages
        return ""

    async def _handle_cek_command(self, phone_number: str, ticker: str) -> str:
        cache_key = f"cek:{ticker}"
        cached_resp = await self.cache.get(cache_key)
        if cached_resp:
            await self.waha.send_text(phone_number, cached_resp)
            return cached_resp

        async with async_session_factory() as session:
            event_repo = EventRepository(session)
            events = await event_repo.get_latest_by_ticker(ticker, limit=3)

        if not events:
            resp = f"ℹ️ Belum ada aksi korporasi strategis atau Konglo Move yang tercatat untuk *${ticker}*."
            await self.waha.send_text(phone_number, resp)
            return resp

        # Use the latest formatted message or compile summary
        latest = events[0]
        resp = latest.wa_formatted_message or f"🚨 *[IDX-INTEL ALERT]*\nEmiten: *${ticker}*\nEvent: {latest.title}"
        await self.cache.set(cache_key, resp)
        await self.waha.send_text(phone_number, resp)
        return resp

    async def _handle_summary_command(self, phone_number: str) -> str:
        cache_key = "summary:latest"
        cached_resp = await self.cache.get(cache_key)
        if cached_resp:
            await self.waha.send_text(phone_number, cached_resp)
            return cached_resp

        async with async_session_factory() as session:
            event_repo = EventRepository(session)
            events = await event_repo.get_recent_events(limit=5)

        if not events:
            resp = "ℹ️ Belum ada ringkasan aksi korporasi strategis terbaru saat ini."
            await self.waha.send_text(phone_number, resp)
            return resp

        lines = ["📈 *RINGKASAN AKSI KORPORASI STRATEGIS & KONGLO MOVE* 📈", "------------------------------------------------"]
        for idx, ev in enumerate(events, 1):
            lines.append(f"{idx}. *${ev.ticker}* [{ev.event_type}]: {ev.title} _({ev.recommendation_class or 'HOLD/WATCH'})_")
        lines.append("------------------------------------------------\nKetik `/cek <TICKER>` untuk detail lengkap.")
        resp = "\n".join(lines)

        await self.cache.set(cache_key, resp)
        await self.waha.send_text(phone_number, resp)
        return resp

    async def _handle_subscribe_command(self, phone_number: str, ticker: str) -> str:
        async with async_session_factory() as session:
            user_repo = UserRepository(session)
            await user_repo.subscribe_ticker(phone_number, ticker)
            await session.commit()

        resp = f"✅ Berhasil subscribe notifikasi aksi korporasi untuk emiten *${ticker}*."
        await self.waha.send_text(phone_number, resp)
        return resp

    async def _handle_unsubscribe_command(self, phone_number: str, ticker: str) -> str:
        async with async_session_factory() as session:
            user_repo = UserRepository(session)
            removed = await user_repo.unsubscribe_ticker(phone_number, ticker)
            await session.commit()

        if removed:
            resp = f"🗑️ Berhasil berhenti berlangganan (unsubscribe) notifikasi *${ticker}*."
        else:
            resp = f"ℹ️ Anda belum terdaftar sebagai subscriber untuk *${ticker}*."
        await self.waha.send_text(phone_number, resp)
        return resp
