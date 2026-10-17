from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.sector_schema import (
    SectorRecommendationsResponse,
    SectorDetailResponse,
)
from app.services.sector_service import SectorIntelligenceService
from app.utils.logger import get_logger

logger = get_logger("routers.us")

router = APIRouter(prefix="/api/v1/us", tags=["US Intelligence"])
sector_service = SectorIntelligenceService()


@router.get(
    "/sectors",
    response_model=SectorRecommendationsResponse,
    summary="Get US Intelligence sector recommendations (S&P 500, NASDAQ, Mega-Tech, Semis, US ETFs)",
    status_code=status.HTTP_200_OK,
)
async def get_us_sectors():
    """
    Returns latest sector recommendations and stances across Wall Street indices,
    leading US sectors, and US-listed benchmark ETFs (SPY, QQQ, DIA, IWM, SMH, XLK, etc.).
    """
    return sector_service.get_latest_recommendations(category="sp500")


@router.get(
    "/sectors/{sector_key}",
    response_model=SectorDetailResponse,
    summary="Get deep-dive recommendations and underlying articles for a US sector",
    status_code=status.HTTP_200_OK,
)
async def get_us_sector_detail(sector_key: str):
    """
    Returns detailed stance, AI thesis, and underlying news articles for a single US sector.
    """
    detail = sector_service.get_sector_detail(category="sp500", sector_key=sector_key)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"US sector '{sector_key}' not found.",
        )
    return detail


@router.post(
    "/scrapers/run",
    summary="Trigger US and global news scrapers (Yahoo Finance, TradingView, CNBC Global)",
    status_code=status.HTTP_200_OK,
)
async def run_us_scrapers(broadcast: bool = Query(default=False, description="Broadcast to US Intel AI WhatsApp channel if true")):
    """
    Executes Yahoo Finance, TradingView, and CNBC Global news scrapers, updates S&P 500 taxonomy,
    and optionally dispatches alert.
    """
    try:
        result = await sector_service.run_full_sector_pipeline(broadcast=broadcast)
        return {
            "status": "success",
            "message": "US sector pipeline executed successfully",
            "articles_scraped": result.articles_scraped,
            "sectors_analyzed": len([r for r in result.recommendations if r.category == "sp500"]),
            "broadcast_sent": result.broadcast_sent.get("us_sent", False),
        }
    except Exception as e:
        logger.error("Failed to run US scraper pipeline", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute US pipeline: {str(e)}",
        )


@router.post(
    "/broadcast",
    summary="Broadcast US sector intelligence to US Intel AI WhatsApp channel",
    status_code=status.HTTP_200_OK,
)
async def broadcast_us_report(target_chat_id: str | None = Query(default=None, description="Optional override WhatsApp Chat ID")):
    """
    Manually triggers formatted WhatsApp alert dispatch to US Intel AI channel.
    """
    success = await sector_service.dispatch_us_report(target_chat_id=target_chat_id)
    return {
        "status": "success" if success else "failed",
        "chat_id_used": target_chat_id or "default_us_channel",
        "delivered": success,
    }
