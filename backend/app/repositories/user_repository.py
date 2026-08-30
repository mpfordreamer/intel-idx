from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user_model import User, UserSubscription
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for managing WhatsApp subscriber accounts and ticker subscriptions.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_unique_key(self, **kwargs: Any) -> User | None:
        phone_number = kwargs.get("phone_number")
        if not phone_number:
            return None
        return await self.get_by_phone(phone_number)

    async def get_by_phone(self, phone_number: str) -> User | None:
        """Fetch user by WhatsApp phone number."""
        stmt = (
            select(User)
            .where(User.phone_number == phone_number)
            .options(selectinload(User.subscriptions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_user(self, phone_number: str) -> User:
        """Fetch existing user or register new WhatsApp account."""
        user = await self.get_by_phone(phone_number)
        if not user:
            user = await self.create(phone_number=phone_number, is_active=True)
        return user

    async def subscribe_ticker(self, phone_number: str, ticker: str) -> UserSubscription:
        """Subscribe user to specific ticker symbol notifications."""
        user = await self.get_or_create_user(phone_number)
        ticker_clean = ticker.upper().lstrip("$")

        # Check if already subscribed
        stmt = select(UserSubscription).where(
            UserSubscription.user_id == user.id,
            UserSubscription.ticker == ticker_clean,
        )
        result = await self.session.execute(stmt)
        subscription = result.scalar_one_or_none()
        if subscription:
            subscription.is_active = True
            await self.session.flush()
            return subscription

        new_sub = UserSubscription(user_id=user.id, ticker=ticker_clean, is_active=True)
        self.session.add(new_sub)
        await self.session.flush()
        await self.session.refresh(new_sub)
        return new_sub

    async def unsubscribe_ticker(self, phone_number: str, ticker: str) -> bool:
        """Unsubscribe user from specific ticker symbol."""
        user = await self.get_by_phone(phone_number)
        if not user:
            return False

        ticker_clean = ticker.upper().lstrip("$")
        stmt = select(UserSubscription).where(
            UserSubscription.user_id == user.id,
            UserSubscription.ticker == ticker_clean,
        )
        result = await self.session.execute(stmt)
        subscription = result.scalar_one_or_none()
        if not subscription:
            return False

        await self.session.delete(subscription)
        await self.session.flush()
        return True

    async def get_subscribers_by_ticker(self, ticker: str) -> list[str]:
        """Returns list of phone numbers subscribed to a specific ticker symbol."""
        stmt = (
            select(User.phone_number)
            .join(UserSubscription, User.id == UserSubscription.user_id)
            .where(
                UserSubscription.ticker == ticker.upper(),
                UserSubscription.is_active.is_(True),
                User.is_active.is_(True),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
