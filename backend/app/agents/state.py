from typing import Any, TypedDict
from app.schemas.event_schema import ScrapedRawDocument


class AgentState(TypedDict, total=False):
    """
    LangGraph StateGraph payload passed across the intelligence pipeline.
    """
    # Input scraped document
    document: ScrapedRawDocument

    # SHA-256 deduplication check
    event_hash: str
    is_duplicate: bool

    # Classifier output
    category: str  # BACKDOOR_LISTING, KONGLO_MOVE, or IRRELEVANT
    confidence_score: float
    reasoning: str

    # Quantitative Extractor output
    extracted_data: dict[str, Any] | None

    # Impact analysis output
    impact_analysis: str | None

    # Recommendation class output
    recommendation_class: str | None

    # Formatted WA message
    wa_formatted_message: str | None

    # Database event ID after saving
    saved_event_id: int | None

    # Notification status
    notified_subscribers_count: int
    error_message: str | None
