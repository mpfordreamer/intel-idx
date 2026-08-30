from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class User(Base):
    """
    Stores WhatsApp user accounts registered with IDX-Intel AI bot.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(
        String(25),
        unique=True,
        index=True,
        nullable=False,
        doc="WhatsApp phone number in E.164 format (e.g. 6281234567890)",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    subscriptions: Mapped[list["UserSubscription"]] = relationship(
        "UserSubscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone_number={self.phone_number})>"


class UserSubscription(Base):
    """
    Tracks specific IDX ticker symbols ($TICKER) a user has subscribed to via /subscribe command.
    """
    __tablename__ = "user_subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_user_ticker_subscription"),
        Index("ix_user_subscriptions_ticker", "ticker"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticker: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="Ticker symbol without $ sign (e.g. BBCA, BUMI, BREN)",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<UserSubscription(user_id={self.user_id}, ticker={self.ticker})>"
