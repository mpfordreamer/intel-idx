from app.agents.state import AgentState
from app.repositories.event_repository import EventRepository
from app.services.prompt import format_wa_alert_message
from app.services.sector_mapping import SP500_TAXONOMY
from app.utils.db_session import async_session_factory
from app.utils.logger import get_logger

logger = get_logger("agents.wa_formatter")


async def wa_formatter_node(state: AgentState) -> dict:
    """
    WA Formatter & Database Persistence Node:
    Formats extracted intelligence into crisp WhatsApp markdown alert
    and saves the ACID CorporateEvent to PostgreSQL.
    """
    doc = state["document"]
    event_hash = state["event_hash"]
    category = state.get("category", "KONGLO_MOVE")
    extracted = state.get("extracted_data")
    impact = state.get("impact_analysis")
    rec_class = state.get("recommendation_class")
    multi_horizon = state.get("multi_horizon")
    invalidation_triggers = state.get("invalidation_triggers")
    action_plan = state.get("action_plan")
    dynamic_narrative = state.get("dynamic_narrative")

    us_tickers = {t for info in SP500_TAXONOMY.values() for t in info.get("tickers", [])}
    is_us = (
        doc.source_name in ("TRADINGVIEW_REALTIME", "YAHOO_FINANCE", "YAHOO_FINANCE_US")
        or doc.ticker.upper() in us_tickers
    )

    wa_msg = format_wa_alert_message(
        ticker=doc.ticker,
        event_type=category,
        title=doc.title,
        extracted_data=extracted,
        impact_analysis=impact,
        recommendation_class=rec_class,
        source_url=doc.source_url,
        raw_text=doc.raw_text,
        multi_horizon=multi_horizon,
        invalidation_triggers=invalidation_triggers,
        action_plan=action_plan,
        dynamic_narrative=dynamic_narrative,
        is_us=is_us,
    )

    saved_id = None
    try:
        async with async_session_factory() as session:
            repo = EventRepository(session)
            existing = await repo.get_by_hash(event_hash)
            if not existing:
                new_event = await repo.create(
                    event_hash=event_hash,
                    ticker=doc.ticker.upper(),
                    event_type=category,
                    title=doc.title,
                    source_url=doc.source_url,
                    publication_date=doc.publication_date,
                    raw_text=doc.raw_text,
                    extracted_json=extracted,
                    impact_analysis=impact,
                    recommendation_class=rec_class,
                    wa_formatted_message=wa_msg,
                )
                await session.commit()
                saved_id = new_event.id
                logger.info("CorporateEvent saved to PostgreSQL", event_id=saved_id, ticker=doc.ticker)
            else:
                saved_id = existing.id
    except Exception as e:
        logger.warning(f"Failed to save CorporateEvent to DB: {e}")

    return {
        "wa_formatted_message": wa_msg,
        "saved_event_id": saved_id,
    }
