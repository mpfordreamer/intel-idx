from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert_log_model import AlertLog
from app.repositories.base_repository import BaseRepository


class AlertLogRepository(BaseRepository[AlertLog]):
    """
    Repository for logging outbound WhatsApp notifications and tracking delivery status.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, AlertLog)

    async def get_by_unique_key(self, **kwargs: Any) -> AlertLog | None:
        """Fetch alert log by primary ID if provided."""
        log_id = kwargs.get("id")
        if not log_id:
            return None
        return await self.get_by_id(log_id)

    async def log_attempt(
        self,
        phone_number: str,
        message_content: str,
        status: str = "PENDING",
        event_id: int | None = None,
        error_message: str | None = None,
    ) -> AlertLog:
        """Create a new alert attempt log record."""
        return await self.create(
            phone_number=phone_number,
            message_content=message_content,
            status=status,
            event_id=event_id,
            error_message=error_message,
        )

    async def update_status(
        self,
        log_id: int,
        status: str,
        error_message: str | None = None,
    ) -> bool:
        """Update delivery status of an existing alert log."""
        log = await self.get_by_id(log_id)
        if not log:
            return False
        log.status = status
        if error_message:
            log.error_message = error_message
        await self.session.flush()
        return True
