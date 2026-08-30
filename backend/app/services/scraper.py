import asyncio
from app.repositories.event_repository import EventRepository, generate_event_hash
from app.schemas.event_schema import ScrapedRawDocument
from app.scrapers import (
    BaseScraper,
    CNBCRSSScraper,
    GoogleNewsRSSScraper,
    IDNFinancialsScraper,
    IDXAnnouncementScraper,
    IPOTNewsScraper,
    KontanRSSScraper,
)
from app.utils.db_session import async_session_factory
from app.utils.logger import get_logger

logger = get_logger("services.scraper")


class ScraperCoordinatorService:
    """
    Coordinates execution of all registered scrapers, filters duplicates via SHA-256 hash,
    and returns only new, unindexed corporate action documents.
    """

    def __init__(self):
        self.scrapers: list[BaseScraper] = [
            IDXAnnouncementScraper(),
            # GoogleNewsRSSScraper(),
            CNBCRSSScraper(),
            KontanRSSScraper(),
            IDNFinancialsScraper(),
            IPOTNewsScraper(),
        ]

    async def collect_new_documents(self) -> list[ScrapedRawDocument]:
        """
        Runs all scrapers concurrently and removes duplicates by checking PostgreSQL.
        """
        logger.info("Starting collection across all scrapers")
        results = await asyncio.gather(*(s.scrape() for s in self.scrapers), return_exceptions=True)

        all_docs: list[ScrapedRawDocument] = []
        for r in results:
            if isinstance(r, list):
                all_docs.extend(r)
            elif isinstance(r, Exception):
                logger.error("Scraper execution threw exception", error=str(r))

        new_docs: list[ScrapedRawDocument] = []
        try:
            async with async_session_factory() as session:
                repo = EventRepository(session)
                for doc in all_docs:
                    event_hash = generate_event_hash(
                        ticker=doc.ticker,
                        event_type="PENDING_CLASSIFICATION",
                        publication_date=doc.publication_date,
                        title=doc.title,
                    )
                    if not await repo.event_exists(event_hash):
                        new_docs.append(doc)
        except Exception as e:
            logger.warning(f"DB unavailable for duplicate check, returning all docs: {e}")
            new_docs = all_docs

        logger.info(
            "Scraper collection finished",
            total_fetched=len(all_docs),
            new_unique_docs=len(new_docs),
        )
        return new_docs
