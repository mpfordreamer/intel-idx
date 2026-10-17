from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import random
from app.agents.state import AgentState
from app.config import get_settings
from app.services.prompt import IMPACT_SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger("agents.impact")
settings = get_settings()


def _fallback_impact_analysis(ticker: str, category: str, extracted: dict | None) -> str:
    """Fallback crisp analytical summary in Indonesian."""
    investor = "-"
    if extracted and extracted.get("investor_or_group"):
        investor = str(extracted.get("investor_or_group"))

    if category == "BACKDOOR_LISTING":
        return (
            f"Injeksi aset dan perubahan kegiatan usaha berpotensi mengubah prospek fundamental ${ticker.upper()} secara drastis. "
            f"Dukungan strategis dari {investor} memberikan kepastian permodalan baru bagi ekspansi jangka panjang."
        )
    investor_info = f"terkait {investor}" if investor and investor != "-" else "pada emiten"
    variations = [
        f"Aktivitas korporasi terdeteksi {investor_info}. Pelaku pasar disarankan mencermati keterbukaan informasi resmi untuk memverifikasi arah transaksi dan dampak fundamentalnya.",
        f"Informasi keterbukaan terdeteksi {investor_info}. Investor diimbau memverifikasi detail transaksi pada prospektus atau laporan resmi emiten guna mengukur eksposur risiko dan dampaknya.",
    ]
    return random.choice(variations)


async def impact_node(state: AgentState) -> dict:
    """
    Impact Analysis Node:
    Generates a crisp 2-3 sentence financial & strategic impact summary in Indonesian.
    """
    doc = state["document"]
    cat = state.get("category", "KONGLO_MOVE")
    extracted = state.get("extracted_data", {})

    try:
        # Enable thinking if it's from BEI official scraper
        is_bei = doc.source_name == "BEI_OFFICIAL"

        # === CPU-Optimized Configuration ===
        # We temporarily disable "thinking" mode because the VRAM is full
        # and Ollama runs on CPU. Thinking on CPU takes too long.
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0,
            api_key=settings.ORCAROUTER_API_KEY,
            base_url=settings.LLM_MODEL_URL,
            timeout=600,
            max_retries=0
        )
        
        # === ARCHIVED: GPU / Thinking Mode Configuration ===
        # To re-activate thinking mode when GPU VRAM is free, comment out the `llm` block above 
        # and uncomment the block below. Note: Ollama automatically switches to GPU if VRAM is available.
        #
        # llm = ChatOpenAI(
        #     model=settings.LLM_MODEL,
        #     temperature=0,
        #     api_key=settings.ORCAROUTER_API_KEY,
        #     base_url=settings.LLM_MODEL_URL,
        #     extra_body={"enable_thinking": is_bei},
        #     timeout=600,
        #     max_retries=0
        # )

        prompt_messages = [
            SystemMessage(content=IMPACT_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Ticker: {doc.ticker}\nCategory: {cat}\n"
                    f"Extracted Data: {extracted}\n\nNews Title: {doc.title}\nText:\n{doc.raw_text[:1000]}"
                )
            ),
        ]
        res = await llm.ainvoke(prompt_messages)
        content_str = res.content if isinstance(res.content, str) else str(res.content)
        return {"impact_analysis": content_str.strip()}
    except Exception as e:
        logger.warning("LLM impact analysis failed, using fallback", error=str(e))
        return {"impact_analysis": _fallback_impact_analysis(doc.ticker, cat, extracted)}
