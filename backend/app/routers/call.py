from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

from app.utils.db_session import async_session_factory
from app.repositories.event_repository import EventRepository
from app.agents.chat import ChatAgentService

router = APIRouter(prefix="/call", tags=["Dynamic LLM Calls"])

class QueryResponse(BaseModel):
    message: str

@router.get("/{ticker}", response_model=QueryResponse)
async def call_ticker(ticker: str):
    """
    Retrieves the latest corporate events for a ticker and generates a dynamic
    WhatsApp-formatted summary using the LLM.
    """
    async with async_session_factory() as session:
        event_repo = EventRepository(session)
        events = await event_repo.get_latest_by_ticker(ticker, limit=3)
        
    # Convert ORM objects to dict
    events_data = []
    for ev in events:
        events_data.append({
            "ticker": ev.ticker,
            "title": ev.title,
            "event_type": ev.event_type,
            "publication_date": ev.publication_date.isoformat() if ev.publication_date else None,
            "recommendation_class": ev.recommendation_class,
            "impact_analysis": ev.impact_analysis
        })
        
    summary = await ChatAgentService.generate_ticker_summary(ticker, events_data)
    return QueryResponse(message=summary)


@router.get("/category/{category_name}", response_model=QueryResponse)
async def call_category(category_name: str):
    """
    Retrieves the latest corporate events for a specific category (e.g. KONGLO_MOVE)
    and generates a dynamic summary using the LLM.
    """
    async with async_session_factory() as session:
        event_repo = EventRepository(session)
        events = await event_repo.get_recent_by_category(category_name.upper(), limit=5)
        
    events_data = []
    for ev in events:
        events_data.append({
            "ticker": ev.ticker,
            "title": ev.title,
            "event_type": ev.event_type,
            "publication_date": ev.publication_date.isoformat() if ev.publication_date else None,
            "impact_analysis": ev.impact_analysis
        })
        
    summary = await ChatAgentService.generate_category_summary(category_name, events_data)
    return QueryResponse(message=summary)


@router.post("/famous", response_model=QueryResponse)
async def call_famous(tickers: List[str]):
    """
    Retrieves the latest corporate events for a list of famous tickers
    and generates a dynamic summary.
    """
    async with async_session_factory() as session:
        event_repo = EventRepository(session)
        events = await event_repo.get_recent_by_tickers([t.upper() for t in tickers], limit=10)
        
    events_data = []
    for ev in events:
        events_data.append({
            "ticker": ev.ticker,
            "title": ev.title,
            "event_type": ev.event_type,
            "publication_date": ev.publication_date.isoformat() if ev.publication_date else None,
            "impact_analysis": ev.impact_analysis
        })
        
    summary = await ChatAgentService.generate_category_summary("Famous Stocks", events_data)
    return QueryResponse(message=summary)
