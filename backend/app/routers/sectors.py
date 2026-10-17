from typing import Literal
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.sector_schema import (
    SectorRecommendationsResponse,
    SectorDetailResponse,
    SectorScrapeAndAnalyzeResponse,
)
from app.services.sector_service import SectorIntelligenceService
from app.utils.logger import get_logger

logger = get_logger("routers.sectors")

router = APIRouter(prefix="/api/v1/sectors", tags=["Sector Intelligence"])
sector_service = SectorIntelligenceService()


@router.get(
    "/recommendations",
    response_model=SectorRecommendationsResponse,
    summary="Get multi-market sector recommendations (IDX, S&P 500, Commodities)",
    status_code=status.HTTP_200_OK,
)
async def get_sector_recommendations(
    category: Literal["commodity", "sp500", "idx"] | None = Query(
        default=None,
        description="Filter recommendations by pillar category (commodity, sp500, or idx)",
    )
):
    """
    Returns latest context-aware sector recommendations.
    All recommendation stances preserve underscore notation (e.g. OVERWEIGHT, ACCUMULATE_ON_WEAKNESS).
    """
    return sector_service.get_latest_recommendations(category=category)


@router.post(
    "/scrape-and-analyze",
    response_model=SectorScrapeAndAnalyzeResponse,
    summary="Trigger real-time multi-market scraping, AI synthesis, and optional WAHA broadcast",
    status_code=status.HTTP_200_OK,
)
async def trigger_scrape_and_analyze(
    broadcast: bool = Query(
        default=False,
        description="If true, sends formatted alerts to respective WhatsApp groups (IDX vs S&P 500)",
    )
):
    """
    Scrapes TradingView, Yahoo Finance, and CNBC real-time feeds,
    maps articles to sectors, runs AI sector synthesis, and updates cached recommendations.
    """
    try:
        result = await sector_service.run_full_sector_pipeline(broadcast=broadcast)
        return result
    except Exception as e:
        logger.error("Sector pipeline execution failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute sector pipeline: {str(e)}",
        )


@router.get(
    "/news/realtime",
    summary="Get real-time news headlines partitioned by sector",
    status_code=status.HTTP_200_OK,
)
async def get_realtime_news():
    """
    Returns raw scraped news items grouped by sector key.
    """
    return sector_service.get_realtime_news()


@router.get(
    "/{category}/{sector_name}",
    response_model=SectorDetailResponse,
    summary="Get deep-dive recommendations and underlying articles for a specific sector",
    status_code=status.HTTP_200_OK,
)
async def get_sector_detail(category: str, sector_name: str):
    """
    Returns recommendation details and underlying news articles for a single sector.
    """
    detail = sector_service.get_sector_detail(category=category, sector_key=sector_name)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector '{sector_name}' in category '{category}' not found.",
        )
    return detail
