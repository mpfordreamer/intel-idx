from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.sector_schema import (
    SectorRecommendationsResponse,
    SectorDetailResponse,
)
from app.services.sector_service import SectorIntelligenceService
from app.utils.logger import get_logger

logger = get_logger("routers.idx")

router = APIRouter(prefix="/api/v1/idx", tags=["IDX Intelligence"])
sector_service = SectorIntelligenceService()


@router.get(
    "/sectors",
    response_model=SectorRecommendationsResponse,
    summary="Get IDX domestic sector intelligence recommendations",
    status_code=status.HTTP_200_OK,
)
async def get_idx_sectors():
    """
    Returns latest sector recommendations and stances across the 11 official BEI sectors.
    """
    return sector_service.get_latest_recommendations(category="idx")


@router.get(
    "/sectors/{sector_key}",
    response_model=SectorDetailResponse,
    summary="Get deep-dive recommendations and underlying articles for an IDX sector",
    status_code=status.HTTP_200_OK,
)
async def get_idx_sector_detail(sector_key: str):
    """
    Returns detailed stance, AI thesis, and underlying news articles for a single IDX sector.
    """
    detail = sector_service.get_sector_detail(category="idx", sector_key=sector_key)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IDX sector '{sector_key}' not found.",
        )
    return detail


@router.post(
    "/scrapers/run",
    summary="Trigger domestic news scrapers and refresh IDX intelligence",
    status_code=status.HTTP_200_OK,
)
async def run_idx_scrapers(broadcast: bool = Query(default=False, description="Broadcast to IDX Intel AI WhatsApp channel if true")):
    """
    Executes domestic news scrapers, analyzes IDX sectors, and optionally dispatches alert.
    """
    try:
        result = await sector_service.run_full_sector_pipeline(broadcast=broadcast)
        return {
            "status": "success",
            "message": "IDX sector pipeline executed successfully",
            "articles_scraped": result.articles_scraped,
            "sectors_analyzed": len([r for r in result.recommendations if r.category == "idx"]),
            "broadcast_sent": result.broadcast_sent.get("idx_sent", False),
        }
    except Exception as e:
        logger.error("Failed to run IDX scraper pipeline", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute IDX pipeline: {str(e)}",
        )


@router.post(
    "/broadcast",
    summary="Broadcast IDX sector intelligence to IDX Intel AI WhatsApp channel",
    status_code=status.HTTP_200_OK,
)
async def broadcast_idx_report(target_chat_id: str | None = Query(default=None, description="Optional override WhatsApp Chat ID")):
    """
    Manually triggers formatted WhatsApp alert dispatch to IDX Intel AI channel.
    """
    success = await sector_service.dispatch_idx_report(target_chat_id=target_chat_id)
    return {
        "status": "success" if success else "failed",
        "chat_id_used": target_chat_id or "default_idx_channel",
        "delivered": success,
    }
