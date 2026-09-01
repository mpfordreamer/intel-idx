from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings
from app.services.prompt import RECOMMENDATION_SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger("agents.recommendation")
settings = get_settings()


def _fallback_recommendation(category: str, extracted: dict | None, title: str, text: str) -> str:
    """
    Deterministic Top 200 Konglomerat rule-based recommendation fallback.
    """
    content_lower = f"{title} {text}".lower()
    investor_group = ""
    if extracted and extracted.get("investor_or_group"):
        investor_group = str(extracted.get("investor_or_group")).lower()

    konglo_keywords = [
        "salim",
        "prajogo",
        "barito",
        "bakrie",
        "djarum",
        "hartono",
        "aguan",
        "agung sedayu",
        "panin",
        "chandra asri",
        "boy thohir",
        "sukanto tanoto",
        "hermanto tanoko",
        "tahir",
        "sinarmas",
        "mach energy",
    ]

    has_konglo = any(k in investor_group for k in konglo_keywords) or any(
        k in content_lower for k in konglo_keywords
    )

    if category in {"BACKDOOR_LISTING", "KONGLO_MOVE"} and has_konglo:
        return "STRONG_BUY_AKUMULASI"
    if category in {"BACKDOOR_LISTING", "KONGLO_MOVE"}:
        return "BUY"
    return "HOLD_WATCH"


async def recommendation_node(state: AgentState) -> dict:
    """
    Recommendation Engine Node:
    Determines final investment recommendation class:
    STRONG_BUY_AKUMULASI (Mandatory for Top 200 Konglomerat/famous business groups),
    BUY, HOLD_WATCH, or AVOID.
    """
    doc = state["document"]
    cat = state.get("category", "KONGLO_MOVE")
    extracted = state.get("extracted_data", {})

    try:
        # Enable thinking if it's from BEI official scraper
        is_bei = doc.source_name == "BEI_OFFICIAL"

        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0,
            api_key=settings.ORCAROUTER_API_KEY,
            base_url=settings.LLM_MODEL_URL,
            extra_body={"enable_thinking": is_bei}
        )
        prompt_messages = [
            SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Ticker: {doc.ticker}\nCategory: {cat}\n"
                    f"Investor/Group: {extracted.get('investor_or_group') if extracted else '-'}\n"
                    f"Title: {doc.title}\nText:\n{doc.raw_text[:800]}"
                )
            ),
        ]
        res = await llm.ainvoke(prompt_messages)
        rec_class = res.content.strip() if isinstance(res.content, str) else str(res.content).strip()
        valid_classes = {"STRONG_BUY_AKUMULASI", "BUY", "HOLD_WATCH", "AVOID"}
        if rec_class not in valid_classes:
            rec_class = _fallback_recommendation(cat, extracted, doc.title, doc.raw_text)
        return {"recommendation_class": rec_class}
    except Exception as e:
        logger.warning("LLM recommendation engine failed, using rule-based fallback", error=str(e))
        return {
            "recommendation_class": _fallback_recommendation(
                cat, extracted, doc.title, doc.raw_text
            )
        }
