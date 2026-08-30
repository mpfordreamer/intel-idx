from fastapi import APIRouter, Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.config import get_settings
from app.schemas.response_schema import APIResponse
from app.services.agent import AgentExecutionService
from app.services.scraper import ScraperCoordinatorService
from app.utils.logger import get_logger
from app.utils.db_session import get_db_session
from app.models.event_model import CorporateEvent

logger = get_logger("routers.monitor")
settings = get_settings()
router = APIRouter(prefix="/api/v1", tags=["Monitoring & Scraping"])

scraper_coordinator = ScraperCoordinatorService()


@router.post("/monitor", status_code=status.HTTP_200_OK)
async def trigger_monitor_cycle(
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
):
    """
    Manually trigger corporate action collection across all 6 scrapers
    and process unindexed documents through the LangGraph AI intelligence pipeline.
    """
    try:
        if settings.API_KEY_SECRET and x_api_key != settings.API_KEY_SECRET:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

        logger.info("Manual monitor cycle triggered")
        new_docs = await scraper_coordinator.collect_new_documents()

        results = []
        for doc in new_docs:
            res = await AgentExecutionService.process_document(doc)
            if res:
                results.append(res)

        logger.info(f"Monitor cycle complete. Processed {len(results)} valid documents.")

        return APIResponse(
            success=True,
            message=f"Processed {len(new_docs)} new corporate action documents",
            data={
                "new_documents_count": len(new_docs),
                "results": results,
            },
        )
    except Exception as e:
        import traceback
        logger.error(f"Error in monitor endpoint: {e}")
        logger.error(traceback.format_exc())
        return APIResponse(
            success=False,
            message=f"Internal Server Error: {e}",
            data=None
        )


@router.get("/events", status_code=status.HTTP_200_OK)
async def get_recent_events(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Fetch the latest 50 analyzed corporate events from the database.
    """
    try:
        stmt = select(CorporateEvent).order_by(desc(CorporateEvent.publication_date)).limit(50)
        result = await db.execute(stmt)
        events = result.scalars().all()
        
        results = []
        for event in events:
            source_name = "Sistem"
            if event.source_url:
                if "idx.co.id" in event.source_url:
                    source_name = "BEI OFFICIAL"
                elif "cnbcindonesia.com" in event.source_url:
                    source_name = "CNBC MARKET RSS"
                elif "news.google.com" in event.source_url:
                    source_name = "GOOGLE NEWS RSS"
                elif "idnfinancials.com" in event.source_url:
                    source_name = "IDN FINANCIALS"
                elif "indopremier.com" in event.source_url or "ipotnews" in event.source_url:
                    source_name = "IPOT NEWS"
                elif "kontan.co.id" in event.source_url:
                    source_name = "KONTAN INVESTASI RSS"
                else:
                    source_name = "Berita Publik"

            results.append({
                "title": event.title,
                "publication_date": event.publication_date.isoformat() if event.publication_date else None,
                "source_name": source_name,
                "ticker": event.ticker,
                "category": event.event_type,
                "recommendation": event.recommendation_class,
                "impact_analysis": event.impact_analysis,
                "wa_formatted_message": event.wa_formatted_message,
                "saved_event_id": str(event.id),
                "notified_count": 0,
            })
            
        return APIResponse(
            success=True,
            message="Fetched recent corporate events",
            data={
                "new_documents_count": 0,
                "results": results,
            },
        )
    except Exception as e:
        import traceback
        logger.error(f"Error in GET /events endpoint: {e}")
        logger.error(traceback.format_exc())
        return APIResponse(
            success=False,
            message=f"Internal Server Error: {e}",
            data=None
        )
