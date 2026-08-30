from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class CorporateEvent(Base):
    """
    Stores extracted corporate action intelligence events from IDX, RSS, and news.
    Enforces ACID uniqueness using SHA-256 event_hash to prevent duplicates.
    """
    __tablename__ = "corporate_events"
    __table_args__ = (
        Index("ix_corporate_events_ticker_event_type", "ticker", "event_type"),
        Index("ix_corporate_events_publication_date", "publication_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        doc="SHA-256 hash of ticker + event_type + publication_date + title for deduplication",
    )
    ticker: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="BACKDOOR_LISTING, KONGLO_MOVE, or IRRELEVANT",
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    publication_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Structured quantitative data extracted by Pydantic schema",
    )
    impact_analysis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Bullish/Bearish/Neutral financial impact & sentiment analysis",
    )
    recommendation_class: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="STRONG_BUY_AKUMULASI, BUY, HOLD_WATCH, or AVOID",
    )
    wa_formatted_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Formatted WhatsApp alert message ready for dispatch",
    )

    def __repr__(self) -> str:
        return f"<CorporateEvent(id={self.id}, ticker={self.ticker}, event_type={self.event_type})>"
