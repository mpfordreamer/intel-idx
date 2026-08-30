from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class ScrapedRawDocument(BaseModel):
    """
    Input DTO representing a raw scraped article or IDX announcement.
    """
    model_config = ConfigDict(extra="ignore")

    ticker: str = Field(..., description="Stock symbol identified in title or text")
    title: str = Field(..., description="Headline of article or announcement")
    source_url: str = Field(..., description="URL of origin source")
    publication_date: datetime = Field(..., description="Publication UTC timestamp")
    raw_text: str = Field(..., description="Full clean text body of document")
    source_name: str = Field(..., description="Name of scraper source (e.g. IDX, CNBC, Kontan)")


class EventClassificationResult(BaseModel):
    """
    Output schema for ClassifierNode LLM decision.
    Strictly categorizes into BACKDOOR_LISTING, KONGLO_MOVE, or IRRELEVANT.
    """
    category: Literal["BACKDOOR_LISTING", "KONGLO_MOVE", "SURPRISE_FUNDAMENTAL", "BIG_CONTRACT", "IRRELEVANT"] = Field(
        ...,
        description="Must be BACKDOOR_LISTING, KONGLO_MOVE, SURPRISE_FUNDAMENTAL, BIG_CONTRACT, or IRRELEVANT",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence in classification decision",
    )
    reasoning: str = Field(
        ...,
        description="Brief explanation of why this event fits the category or was rejected as IRRELEVANT",
    )


class ExtractedEventData(BaseModel):
    """
    Structured quantitative parameters extracted by ExtractorNode using Pydantic structured output.
    """
    action_type: str = Field(
        ...,
        description="Specific corporate action (e.g. Crossing Pasar Negosiasi, Private Placement, Reverse Takeover)",
    )
    investor_or_group: str | None = Field(
        default=None,
        description="Name of Konglomerat / Smart Money / Investor Group involved (e.g. Prajogo Pangestu, Salim, Bakrie)",
    )
    execution_price_idr: float | None = Field(
        default=None,
        description="Execution or transaction price per share in IDR",
    )
    transaction_value_idr: float | None = Field(
        default=None,
        description="Total transaction value in IDR",
    )
    ownership_percentage: float | None = Field(
        default=None,
        description="Percentage of ownership acquired or held",
    )
    key_dates: dict[str, str] | None = Field(
        default=None,
        description="Important dates (cum_date, ex_date, recording_date, execution_date)",
    )
    additional_metadata: dict[str, Any] | None = Field(
        default=None,
        description="Any extra quantitative terms or ratios",
    )
