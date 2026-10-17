from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class SectorNewsItem(BaseModel):
    title: str
    source_name: str
    source_url: str
    publication_date: datetime
    ticker: str
    summary_snippet: str | None = None


class SectorRecommendationItem(BaseModel):
    sector_key: str
    sector_name: str
    category: Literal["commodity", "sp500", "idx"]
    stance: Literal[
        "OVERWEIGHT",
        "NEUTRAL",
        "UNDERWEIGHT",
        "ACCUMULATE_ON_WEAKNESS",
        "HOLD_WATCH",
        "AVOID",
        "STRONG_BUY_AKUMULASI",
        "BUY",
        "HOLD",
    ] = Field(description="Preserves underscore label formatting")
    recommendation: Literal["BUY", "HOLD", "AVOID"] = Field(default="HOLD", description="Action recommendation BUY, HOLD, or AVOID")
    score: float = Field(ge=-1.0, le=1.0, description="Sentiment/momentum score from -1.0 to +1.0")
    conviction_score: int = Field(default=75, ge=50, le=98, description="AI-calculated conviction percentage (50-98%)")
    ai_analysis: str = Field(description="Dynamic AI-synthesized contextual reasoning")
    detected_tickers: list[str] = Field(default_factory=list, description="Actual stock or ETF tickers detected from news")
    top_picks: list[str] = Field(default_factory=list, description="Recommended tickers or symbols")
    catalysts: list[str] = Field(default_factory=list, description="Real drivers and market catalysts")
    risk_factors: list[str] = Field(default_factory=list, description="Downside risk factors and headwinds")
    news_count: int = Field(default=0, description="Number of real-time articles analyzed for this sector")


class SectorRecommendationsResponse(BaseModel):
    timestamp: datetime
    total_sectors: int
    recommendations: list[SectorRecommendationItem]
    executive_summary: str | None = None


class SectorDetailResponse(BaseModel):
    sector_key: str
    sector_name: str
    category: Literal["commodity", "sp500", "idx"]
    recommendation: SectorRecommendationItem
    articles: list[SectorNewsItem]


class SectorScrapeAndAnalyzeResponse(BaseModel):
    status: str
    articles_scraped: int
    sectors_analyzed: int
    broadcast_sent: dict[str, Any]
    recommendations: list[SectorRecommendationItem]
