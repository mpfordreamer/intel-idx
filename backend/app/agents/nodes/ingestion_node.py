from app.agents.state import AgentState
from app.repositories.event_repository import EventRepository, generate_event_hash
from app.utils.db_session import async_session_factory
from app.utils.logger import get_logger

logger = get_logger("agents.ingestion")


async def ingestion_node(state: AgentState) -> dict:
    """
    Ingestion & Deduplication Node:
    Computes SHA-256 event_hash and checks PostgreSQL if this event has already been processed.
    """
    doc = state["document"]
    event_hash = generate_event_hash(
        ticker=doc.ticker,
        event_type="PENDING_CLASSIFICATION",
        publication_date=doc.publication_date,
        title=doc.title,
    )

    is_dup = False
    try:
        async with async_session_factory() as session:
            repo = EventRepository(session)
            is_dup = await repo.event_exists(event_hash)
    except Exception as e:
        logger.warning(f"Failed to connect to DB for deduplication check: {e}")

    if is_dup:
        logger.info(
            "Duplicate event detected during ingestion",
            ticker=doc.ticker,
            event_hash=event_hash,
        )

    return {
        "event_hash": event_hash,
        "is_duplicate": is_dup,
    }
