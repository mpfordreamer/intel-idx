import pytest
from app.services.notification import RateLimiter, RedisCommandCache


@pytest.mark.asyncio
async def test_in_memory_rate_limiter():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    phone = "62811111111"

    # First request -> OK
    assert not await limiter.is_rate_limited(phone)
    # Second request -> OK
    assert not await limiter.is_rate_limited(phone)
    # Third request -> Throttled!
    assert await limiter.is_rate_limited(phone)


@pytest.mark.asyncio
async def test_command_cache_fallback():
    cache = RedisCommandCache(ttl_seconds=5)
    key = "cek:BBCA"
    value = "🚨 *BBCA*: Laporan Corporate Action"

    # Cache should be empty initially
    assert await cache.get(key) is None

    # Set and get from cache
    await cache.set(key, value)
    assert await cache.get(key) == value
