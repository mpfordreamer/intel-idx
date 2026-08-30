from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class AlertLog(Base):
    """
    Logs outbound WhatsApp notifications dispatched via WAHA HTTP API.
    Tracks delivery statuses: PENDING, SENT, or FAILED.
    """
    __tablename__ = "alert_logs"
    __table_args__ = (
        Index("ix_alert_logs_status", "status"),
        Index("ix_alert_logs_phone_number", "phone_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("corporate_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(String(25), nullable=False)
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False,
        doc="PENDING, SENT, or FAILED",
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<AlertLog(id={self.id}, phone_number={self.phone_number}, status={self.status})>"
