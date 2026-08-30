from app.agents import run_intelligence_pipeline
from app.schemas.event_schema import ScrapedRawDocument
from app.utils.logger import get_logger

logger = get_logger("services.agent")


class AgentExecutionService:
    """
    Service wrapper around LangGraph intelligence pipeline for easy invocation by schedulers and routers.
    """

    @classmethod
    async def process_document(cls, document: ScrapedRawDocument) -> dict | None:
        """
        Executes LangGraph pipeline for a single ScrapedRawDocument and returns execution metrics.
        """
        if "UNKNOWN" in document.ticker.upper():
            logger.info(f"Skipping processing for UNKNOWN ticker: {document.title}")
            return None

        try:
            result_state = await run_intelligence_pipeline(document)
            return {
                "title": document.title,
                "publication_date": document.publication_date.isoformat() if document.publication_date else None,
                "source_name": document.source_name,
                "ticker": document.ticker,
                "category": result_state.get("category", "IRRELEVANT"),
                "recommendation": result_state.get("recommendation_class"),
                "impact_analysis": result_state.get("impact_analysis"),
                "wa_formatted_message": result_state.get("wa_formatted_message"),
                "saved_event_id": str(result_state.get("saved_event_id")) if result_state.get("saved_event_id") else None,
                "notified_count": result_state.get("notified_subscribers_count", 0),
            }
        except Exception as e:
            logger.error(f"Pipeline failed for {document.ticker}: {e}")
            return {
                "title": document.title,
                "publication_date": document.publication_date.isoformat() if document.publication_date else None,
                "source_name": document.source_name,
                "ticker": document.ticker,
                "category": "ERROR",
                "recommendation": None,
                "impact_analysis": f"Error: {e}",
                "wa_formatted_message": None,
                "saved_event_id": None,
                "notified_count": 0,
            }
