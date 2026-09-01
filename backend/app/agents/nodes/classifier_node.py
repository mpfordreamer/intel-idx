import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings
from app.schemas.event_schema import EventClassificationResult
from app.services.prompt import CLASSIFIER_SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger("agents.classifier")
settings = get_settings()


def _fallback_keyword_classify(ticker: str, title: str, text: str) -> EventClassificationResult:
    """
    Deterministic keyword rule-based fallback classifier when API key is missing or testing.
    Adheres strictly to the 3-category rule: BACKDOOR_LISTING, KONGLO_MOVE, IRRELEVANT.
    """
    content_lower = f"{title} {text}".lower()

    # 1. Backdoor Listing keywords
    backdoor_kws = ["backdoor listing", "backdoor", "injeksi aset", "reverse takeover", "perusahaan cangkang", "dormant"]
    if any(kw in content_lower for kw in backdoor_kws):
        return EventClassificationResult(
            category="BACKDOOR_LISTING",
            confidence_score=0.92,
            reasoning="Keyword-based detection of Backdoor Listing / Asset Injection.",
        )

    # 2. Konglo Move keywords
    konglo_kws = [
        "salim",
        "prajogo pangestu",
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
        "crossing pasar negosiasi",
        "private placement jumbo",
        "akuisi psp",
        "smart money",
        "akumulasi strategis",
    ]
    if any(kw in content_lower for kw in konglo_kws):
        return EventClassificationResult(
            category="KONGLO_MOVE",
            confidence_score=0.90,
            reasoning="Keyword-based detection of Top 200 Konglomerat / Smart Money accumulation.",
        )

    # 3. Earnings / Financial Report keywords
    earnings_kws = ["laba bersih", "keuntungan", "laporan keuangan", "kinerja keuangan", "laba berjalan", "rugi bersih"]
    if any(kw in content_lower for kw in earnings_kws):
        return EventClassificationResult(
            category="SURPRISE_FUNDAMENTAL",
            confidence_score=0.90,
            reasoning="Keyword-based detection of Financial / Earnings report.",
        )

    # 4. Otherwise IRRELEVANT (Aturan Ketat)
    return EventClassificationResult(
        category="IRRELEVANT",
        confidence_score=0.95,
        reasoning="Does not contain Backdoor Listing or Top Konglomerat accumulation criteria.",
    )


async def classifier_node(state: AgentState) -> dict:
    """
    Classifier Node:
    Strictly categorizes news/announcement into BACKDOOR_LISTING, KONGLO_MOVE, or IRRELEVANT
    using Pydantic structured output with LLM.
    """
    doc = state["document"]

    try:
        # Enable thinking if it's from BEI official scraper
        is_bei = doc.source_name == "BEI_OFFICIAL"

        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0,
            api_key=settings.ORCAROUTER_API_KEY,
            base_url=settings.LLM_MODEL_URL,
            extra_body={"enable_thinking": is_bei}
        ).with_structured_output(EventClassificationResult)

        prompt_messages = [
            SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Ticker: {doc.ticker}\nTitle: {doc.title}\nSource: {doc.source_name}\n\nContent:\n{doc.raw_text}"
            ),
        ]
        result: EventClassificationResult = await llm.ainvoke(prompt_messages)
        logger.info(
            "Event classified successfully",
            ticker=doc.ticker,
            category=result.category,
            confidence=result.confidence_score,
        )
        return {
            "category": result.category,
            "confidence_score": result.confidence_score,
            "reasoning": result.reasoning,
        }
    except Exception as e:
        logger.warning("LLM classifier failed, falling back to keyword rules", error=str(e))
        res = _fallback_keyword_classify(doc.ticker, doc.title, doc.raw_text)
        return {
            "category": res.category,
            "confidence_score": res.confidence_score,
            "reasoning": res.reasoning,
        }
