from fastapi import APIRouter, Header, HTTPException, status
from app.config import get_settings
from app.schemas.response_schema import APIResponse
from app.schemas.waha_schema import WAHAMessagePayload, WAHAWebhookPayload
from app.services.notification import NotificationCommandService
from app.utils.logger import get_logger

logger = get_logger("routers.webhook")
settings = get_settings()
router = APIRouter(prefix="/webhook", tags=["WAHA Webhook"])

notification_service = NotificationCommandService()


@router.post("/waha", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def waha_webhook_handler(
    payload: WAHAWebhookPayload,
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
):
    """
    Receives incoming webhook events from WAHA WhatsApp container.
    Processes interactive commands (/cek, /summary, /subscribe, /unsubscribe).
    """
    if settings.API_KEY_SECRET and x_api_key != settings.API_KEY_SECRET:
        logger.warning("Unauthorized webhook request attempt")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    event_type = payload.event
    if event_type != "message":
        return APIResponse(success=True, message=f"Ignored non-message event: {event_type}")

    if isinstance(payload.payload, dict):
        try:
            msg_payload = WAHAMessagePayload.model_validate(payload.payload)
        except Exception:
            return APIResponse(success=True, message="Invalid message payload format")
    else:
        msg_payload = payload.payload

    logger.info(f">>>>> WHATSAPP_GROUP_ID_DETECTED: {msg_payload.from_} <<<<<")
    if msg_payload.fromMe:
        return APIResponse(success=True, message="Ignored message sent by bot itself")

    phone_number = msg_payload.from_.split("@")[0]
    response_text = await notification_service.process_incoming_command(
        phone_number=phone_number,
        text=msg_payload.body,
    )

    return APIResponse(
        success=True,
        message="Command processed" if response_text else "No interactive command detected",
        data={"sender": phone_number, "response_sent": bool(response_text)},
    )
