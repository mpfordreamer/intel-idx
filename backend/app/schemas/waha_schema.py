from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class WAHAMessagePayload(BaseModel):
    """
    Represents an incoming WhatsApp message inside a WAHA webhook event.
    """
    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Message ID in WAHA")
    timestamp: int | None = Field(default=None, description="Unix timestamp of message")
    from_: str = Field(..., alias="from", description="Sender WhatsApp ID (e.g., 6281234567890@c.us)")
    body: str = Field(..., description="Text content of the incoming message")
    fromMe: bool = Field(default=False, description="Whether message was sent by bot itself")


class WAHAWebhookPayload(BaseModel):
    """
    Root webhook payload dispatched by WAHA container.
    """
    model_config = ConfigDict(extra="ignore")

    event: str = Field(..., description="Event type name (e.g. 'message', 'session.status')")
    session: str = Field(default="default", description="WAHA session name")
    payload: WAHAMessagePayload | dict[str, Any] = Field(..., description="Event data payload")


class WAHASendTextRequest(BaseModel):
    """
    Request body for sending outbound WhatsApp text message via WAHA API endpoint /api/sendText.
    """
    chatId: str = Field(..., description="Recipient chat ID (e.g., 6281234567890@c.us)")
    text: str = Field(..., description="Markdown-formatted message text")
    session: str = Field(default="default", description="Active WAHA session")
