import hashlib
from datetime import datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event_model import CorporateEvent
from app.repositories.base_repository import BaseRepository


def generate_event_hash(ticker: str, event_type: str, publication_date: datetime, title: str) -> str:
    """
    Generates a deterministic SHA-256 hash for corporate event deduplication.
    Formula: SHA256(ticker.upper() + event_type.upper() + publication_date.isoformat() + title.strip().lower())
    """
    raw_payload = f"{ticker.upper()}|{event_type.upper()}|{publication_date.isoformat()}|{title.strip().lower()}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


class EventRepository(BaseRepository[CorporateEvent]):
    """
    Repository for CorporateEvent queries with SHA-256 deduplication checks.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, CorporateEvent)

    async def get_by_unique_key(self, **kwargs: Any) -> CorporateEvent | None:
        """Fetch CorporateEvent by SHA-256 event_hash."""
        event_hash = kwargs.get("event_hash")
        if not event_hash:
            return None
        return await self.get_by_hash(event_hash)

    async def get_by_hash(self, event_hash: str) -> CorporateEvent | None:
        """Fetch CorporateEvent by its unique SHA-256 hash."""
        stmt = select(CorporateEvent).where(CorporateEvent.event_hash == event_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def event_exists(self, event_hash: str) -> bool:
        """Returns True if event with given SHA-256 hash already exists in PostgreSQL."""
        event = await self.get_by_hash(event_hash)
        return event is not None

    async def get_latest_by_ticker(self, ticker: str, limit: int = 5) -> list[CorporateEvent]:
        """Fetch latest corporate events for a given ticker symbol (for /cek <TICKER> command)."""
        stmt = (
            select(CorporateEvent)
            .where(CorporateEvent.ticker == ticker.upper())
            .order_by(CorporateEvent.publication_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_events(self, limit: int = 20) -> list[CorporateEvent]:
        """Fetch latest corporate actions across all tickers (for /summary command)."""
        stmt = (
            select(CorporateEvent)
            .where(CorporateEvent.event_type.in_(["BACKDOOR_LISTING", "KONGLO_MOVE"]))
            .order_by(CorporateEvent.publication_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
