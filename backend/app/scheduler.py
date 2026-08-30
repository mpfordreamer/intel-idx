import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime, timezone, timedelta

from app.scrapers.idx_announcement_scraper import IDXAnnouncementScraper
from app.scrapers.google_news_rss_scraper import GoogleNewsRSSScraper
from app.scrapers.cnbc_rss_scraper import CNBCRSSScraper
from app.scrapers.kontan_rss_scraper import KontanRSSScraper
from app.services.agent import AgentExecutionService
from app.utils.logger import get_logger

logger = get_logger("app.scheduler")

# Instantiate working scrapers
scrapers = [
    IDXAnnouncementScraper(),
    GoogleNewsRSSScraper(),
    CNBCRSSScraper(),
    KontanRSSScraper()
]

async def run_all_scrapers():
    """
    Executes all active scrapers asynchronously and collects the results.
    """
    logger.info("Starting automated scraping cycle...")
    
    tasks = [scraper.scrape() for scraper in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_docs = 0
    wita_tz = timezone(timedelta(hours=8))
    today_wita = datetime.now(wita_tz).date()

    for idx, res in enumerate(results):
        if isinstance(res, Exception):
            logger.error(f"Scraper {scrapers[idx].source_name} failed with exception: {res}")
        elif isinstance(res, list):
            logger.info(f"Scraper {scrapers[idx].source_name} scraped {len(res)} documents.")
            total_docs += len(res)
            
            # Process each document through the AI intelligence pipeline
            for doc in res:
                try:
                    # Filter by WITA "today"
                    doc_date_wita = doc.publication_date.astimezone(wita_tz).date()
                    if doc_date_wita < today_wita:
                        continue
                        
                    await AgentExecutionService.process_document(doc)
                except Exception as e:
                    logger.error(f"AI Pipeline failed for {doc.ticker}", error=str(e))
    logger.info(f"Finished scraping cycle. Total documents fetched: {total_docs}")

# Global scheduler instance
scheduler = AsyncIOScheduler()
scheduler.add_job(run_all_scrapers, 'cron', minute='*/5')
