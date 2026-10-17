import httpx
from app.agents.state import AgentState
from app.config import get_settings
from app.repositories.alert_log_repository import AlertLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.waha_schema import WAHASendTextRequest
from app.services.sector_mapping import SP500_TAXONOMY
from app.utils.db_session import async_session_factory
from app.utils.errors import is_token_or_quota_error
from app.utils.logger import get_logger

logger = get_logger("agents.notification")
settings = get_settings()


async def notification_node(state: AgentState) -> dict:
    """
    Notification Node:
    Queries subscribers for the ticker from PostgreSQL,
    sends formatted WA message via WAHA HTTP API (/api/sendText),
    and records outbound attempts in AlertLog.
    """
    doc = state["document"]
    wa_msg = state.get("wa_formatted_message", "")
    event_id = state.get("saved_event_id")

    if not wa_msg or not wa_msg.strip() or is_token_or_quota_error(wa_msg):
        logger.warning(
            "🛑 [TOKEN HABIS / OUTBOUND SUPPRESSED] Alert dibatalkan dari WhatsApp karena pesan kosong atau terindikasi token/kuota habis.",
            ticker=doc.ticker,
        )
        return {"notified_subscribers_count": 0}

    subscribers: list[str] = []
    try:
        async with async_session_factory() as session:
            user_repo = UserRepository(session)
            subscribers = await user_repo.get_subscribers_by_ticker(doc.ticker)
    except Exception as e:
        logger.warning(f"Failed to fetch subscribers from DB: {e}")

    # Determine broadcast channel: US channel for US equities, IDX channel for BEI
    us_tickers = {t for info in SP500_TAXONOMY.values() for t in info.get("tickers", [])}
    is_us = (
        doc.source_name in ("TRADINGVIEW_REALTIME", "YAHOO_FINANCE", "YAHOO_FINANCE_US")
        or doc.ticker.upper() in us_tickers
    )
    broadcast_target = (settings.BROADCAST_CHAT_ID_SP500 or settings.BROADCAST_CHAT_ID) if is_us else settings.BROADCAST_CHAT_ID

    if broadcast_target and broadcast_target not in subscribers:
        subscribers.append(broadcast_target)

    if not subscribers:
        logger.info("No active subscribers or broadcast chat for ticker", ticker=doc.ticker)
        return {"notified_subscribers_count": 0}

    sent_count = 0
    async with httpx.AsyncClient(timeout=10.0) as http_client:
        for phone in subscribers:
            chat_id = phone if "@" in phone else f"{phone}@c.us"
            payload = WAHASendTextRequest(
                chatId=chat_id,
                text=wa_msg,
                session=settings.WAHA_SESSION,
            )

            status = "PENDING"
            err_msg = None

            headers = {}
            if settings.WAHA_API_KEY:
                headers["X-Api-Key"] = settings.WAHA_API_KEY

            try:
                resp = await http_client.post(
                    f"{settings.WAHA_API_URL}/api/sendText",
                    json=payload.model_dump(),
                    headers=headers,
                )
                if resp.status_code in {200, 201}:
                    status = "SENT"
                    sent_count += 1
                else:
                    status = "FAILED"
                    err_msg = f"HTTP {resp.status_code}: {resp.text}"
            except Exception as e:
                status = "FAILED"
                err_msg = str(e)
                logger.error("Failed to send WAHA alert", phone=phone, error=str(e))

            # Record AlertLog in PostgreSQL
            try:
                async with async_session_factory() as session:
                    log_repo = AlertLogRepository(session)
                    await log_repo.log_attempt(
                        phone_number=phone,
                        message_content=wa_msg,
                        status=status,
                        event_id=event_id,
                        error_message=err_msg,
                    )
                    await session.commit()
            except Exception as db_err:
                logger.error("Failed to save AlertLog", error=str(db_err))

    logger.info(
        "Notification node completed",
        ticker=doc.ticker,
        sent_count=sent_count,
        total_subscribers=len(subscribers),
    )

    return {"notified_subscribers_count": sent_count}
