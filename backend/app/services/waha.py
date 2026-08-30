import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import get_settings
from app.schemas.waha_schema import WAHASendTextRequest
from app.utils.logger import get_logger

logger = get_logger("services.waha")
settings = get_settings()


class WAHAClient:
    """
    HTTP Client for interacting with WAHA (WhatsApp HTTP API) container.
    Includes tenacity retry with exponential backoff.
    """

    def __init__(self):
        self.api_url = settings.WAHA_API_URL
        self.session_name = settings.WAHA_SESSION

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        reraise=True,
    )
    async def send_text(self, chat_id: str, text: str) -> bool:
        """
        Sends an outbound text message to a WhatsApp chat or phone number via WAHA.
        """
        payload = WAHASendTextRequest(
            chatId=chat_id if "@" in chat_id else f"{chat_id}@c.us",
            text=text,
            session=self.session_name,
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.api_url}/api/sendText",
                json=payload.model_dump(),
                headers={"X-Api-Key": settings.WAHA_API_KEY}
            )
            if resp.status_code in {200, 201}:
                logger.info("Message sent via WAHA successfully", chat_id=chat_id)
                return True
            logger.error("WAHA sendText failed", status_code=resp.status_code, text=resp.text)
            resp.raise_for_status()
            return False
