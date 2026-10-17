from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.sector_schema import (
    SectorRecommendationsResponse,
    SectorDetailResponse,
)
from app.services.sector_service import SectorIntelligenceService
from app.utils.logger import get_logger

logger = get_logger("routers.macro")

router = APIRouter(prefix="/api/v1/macro", tags=["Global Macro and Commodities"])
sector_service = SectorIntelligenceService()


@router.get(
    "/commodities",
    response_model=SectorRecommendationsResponse,
    summary="Get 12 Global Commodities intelligence and momentum recommendations",
    status_code=status.HTTP_200_OK,
)
async def get_commodities():
    """
    Returns latest stance, AI analysis, and proxy instruments/ETFs for 12 key global commodities:
    Gold, Silver, Copper, Aluminium, Nickel, Tin, Coal, Crude Oil, CPO, Natural Gas, Lithium, and Uranium.
    """
    return sector_service.get_latest_recommendations(category="commodity")


@router.get(
    "/commodities/{commodity_key}",
    response_model=SectorDetailResponse,
    summary="Get deep-dive recommendations and underlying articles for a specific commodity",
    status_code=status.HTTP_200_OK,
)
async def get_commodity_detail(commodity_key: str):
    """
    Returns detailed stance, AI thesis, and underlying news articles for a single commodity.
    """
    detail = sector_service.get_sector_detail(category="commodity", sector_key=commodity_key)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity '{commodity_key}' not found.",
        )
    return detail


@router.get(
    "/news",
    summary="Get real-time global macroeconomic news (CPI, The Fed, USD/DXY, Trump Trade Tariffs)",
    status_code=status.HTTP_200_OK,
)
async def get_macro_news():
    """
    Returns real-time global macroeconomic and commodity news headlines.
    """
    all_news = sector_service.get_realtime_news()
    macro_news = {}
    for sec_key, items in all_news.items():
        if any(kw in sec_key.lower() for kw in ["macro", "gold", "oil", "copper", "tin", "nickel", "coal", "cpo"]):
            macro_news[sec_key] = items
    return macro_news or all_news


@router.post(
    "/broadcast",
    summary="Broadcast Global Macro & Commodities report to Ternak Saham News WhatsApp channel",
    status_code=status.HTTP_200_OK,
)
async def broadcast_macro_report(target_chat_id: str | None = Query(default=None, description="Optional override WhatsApp Chat ID")):
    """
    Manually triggers formatted WhatsApp alert dispatch to Ternak Saham News channel.
    """
    success = await sector_service.dispatch_ternak_news_report(target_chat_id=target_chat_id)
    return {
        "status": "success" if success else "failed",
        "chat_id_used": target_chat_id or "default_ternak_news_channel",
        "delivered": success,
    }
