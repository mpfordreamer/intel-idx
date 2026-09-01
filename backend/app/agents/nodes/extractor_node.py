import re
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings
from app.schemas.event_schema import ExtractedEventData
from app.services.prompt import EXTRACTOR_SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger("agents.extractor")
settings = get_settings()


def _fallback_regex_extract(title: str, text: str) -> dict[str, Any]:
    """
    Regex fallback extractor for execution price, transaction value, and Konglo investor group.
    """
    content = f"{title}\n{text}"
    data: dict[str, Any] = {
        "action_type": "Corporate Action / Crossing",
        "investor_or_group": None,
        "execution_price_idr": None,
        "transaction_value_idr": None,
        "ownership_percentage": None,
        "key_dates": {},
        "additional_metadata": {},
    }

    # Detect Konglomerat name
    konglo_list = [
        ("Grup Salim", r"\b(?:salim|mach energy|anthony salim)\b"),
        ("Grup Barito / Prajogo Pangestu", r"\b(?:prajogo|barito|chandra asri|bren|cdia)\b"),
        ("Grup Bakrie", r"\b(?:bakrie|bumi|brms)\b"),
        ("Grup Djarum / Hartono", r"\b(?:djarum|hartono|bbca|sarana menara)\b"),
        ("Agung Sedayu / Aguan", r"\b(?:aguan|agung sedayu|pantai indah kapuk)\b"),
        ("Panin Group", r"\b(?:panin|mukmin ali)\b"),
        ("Hermanto Tanoko", r"\b(?:hermanto tanoko|avrs|cleo)\b"),
    ]
    for group_name, pattern in konglo_list:
        if re.search(pattern, content, re.IGNORECASE):
            data["investor_or_group"] = group_name
            break

    # Price per share
    price_match = re.search(r"Rp\s*([\d\.\,]+)\s*(?:/|\s+per\s+)?saham", content, re.IGNORECASE)
    if price_match:
        try:
            raw_num = price_match.group(1).replace(".", "").replace(",", ".")
            data["execution_price_idr"] = float(raw_num)
        except Exception:
            pass

    # Transaction value in Triliun or Miliar
    tril_match = re.search(r"Rp\s*([\d\.\,]+)\s*Triliun", content, re.IGNORECASE)
    if tril_match:
        try:
            raw_num = tril_match.group(1).replace(",", ".")
            data["transaction_value_idr"] = float(raw_num) * 1_000_000_000_000
        except Exception:
            pass
    else:
        miliar_match = re.search(r"Rp\s*([\d\.\,]+)\s*Miliar", content, re.IGNORECASE)
        if miliar_match:
            try:
                raw_num = miliar_match.group(1).replace(",", ".")
                data["transaction_value_idr"] = float(raw_num) * 1_000_000_000
            except Exception:
                pass

    # Ownership percentage
    pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%", content)
    if pct_match:
        try:
            data["ownership_percentage"] = float(pct_match.group(1))
        except Exception:
            pass

    return data


async def extractor_node(state: AgentState) -> dict:
    """
    Extractor Node:
    Extracts quantitative financial facts (execution price, transaction value, ownership %, investor group)
    using LLM structured output or regex fallback.
    """
    doc = state["document"]

    try:
        # Enable thinking if it's from BEI official scraper
        is_bei = doc.source_name == "BEI_OFFICIAL"

        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.2,
            api_key=settings.ORCAROUTER_API_KEY,
            base_url=settings.LLM_MODEL_URL,
            extra_body={"enable_thinking": is_bei}
        ).with_structured_output(ExtractedEventData)

        prompt_messages = [
            SystemMessage(content=EXTRACTOR_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Title: {doc.title}\nCategory: {state.get('category')}\n\nText:\n{doc.raw_text}"
            ),
        ]
        res: ExtractedEventData = await llm.ainvoke(prompt_messages)
        return {"extracted_data": res.model_dump()}
    except Exception as e:
        logger.warning("LLM extractor failed, using fallback regex extractor", error=str(e))
        return {"extracted_data": _fallback_regex_extract(doc.title, doc.raw_text)}
