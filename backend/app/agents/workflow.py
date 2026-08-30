from langgraph.graph import END, START, StateGraph
from app.agents.nodes.classifier_node import classifier_node
from app.agents.nodes.extractor_node import extractor_node
from app.agents.nodes.impact_node import impact_node
from app.agents.nodes.ingestion_node import ingestion_node
from app.agents.nodes.notification_node import notification_node
from app.agents.nodes.recommendation_node import recommendation_node
from app.agents.nodes.wa_formatter_node import wa_formatter_node
from app.agents.state import AgentState
from app.schemas.event_schema import ScrapedRawDocument
from app.utils.logger import get_logger
from app.config import get_settings

logger = get_logger("agents.workflow")
settings = get_settings()


def _should_continue_after_ingestion(state: AgentState) -> str:
    """If event is duplicate, stop processing immediately."""
    if state.get("is_duplicate", False):
        return END
    return "classifier"


def _should_continue_after_classification(state: AgentState) -> str:
    """
    If classification is IRRELEVANT, route directly to wa_formatter to archive it in DB.
    Only proceed to extractor for BACKDOOR_LISTING or KONGLO_MOVE.
    """
    category = state.get("category", "IRRELEVANT")
    if category == "IRRELEVANT":
        return "wa_formatter"
    return "extractor"


def _should_notify(state: AgentState) -> str:
    """
    If category is IRRELEVANT, do not send to WhatsApp (end workflow after archiving).
    """
    category = state.get("category", "IRRELEVANT")
    if category == "IRRELEVANT":
        return END
    return "notification"


def build_idx_intel_workflow():
    """
    Builds and compiles the LangGraph StateGraph intelligence workflow.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("extractor", extractor_node)
    workflow.add_node("impact", impact_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("wa_formatter", wa_formatter_node)
    workflow.add_node("notification", notification_node)

    # Define edges & conditional branches
    workflow.add_edge(START, "ingestion")
    workflow.add_conditional_edges("ingestion", _should_continue_after_ingestion, ["classifier", END])
    workflow.add_conditional_edges("classifier", _should_continue_after_classification, ["extractor", "wa_formatter"])
    workflow.add_edge("extractor", "impact")
    workflow.add_edge("impact", "recommendation")
    workflow.add_edge("recommendation", "wa_formatter")
    workflow.add_conditional_edges("wa_formatter", _should_notify, ["notification", END])
    workflow.add_edge("notification", END)

    return workflow.compile()


async def run_intelligence_pipeline(document: ScrapedRawDocument) -> AgentState:
    """
    Orchestrates the complete IDX-Intel AI agent pipeline for an incoming scraped document.
    Returns the final state.
    """
    app = build_idx_intel_workflow()
    initial_state: AgentState = {
        "document": document,
        "notified_subscribers_count": 0,
    }
    logger.info("Starting intelligence pipeline", ticker=document.ticker, title=document.title)
    final_state = await app.ainvoke(initial_state)
    logger.info(
        "Intelligence pipeline finished",
        ticker=document.ticker,
        category=final_state.get("category", "N/A"),
        recommendation=final_state.get("recommendation_class", "N/A"),
    )
    return final_state
