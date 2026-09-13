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

# Global background queue for scraped documents
DOCUMENT_QUEUE: asyncio.Queue = asyncio.Queue()

async def _document_queue_worker():
    """
    Consumes the DOCUMENT_QUEUE sequentially.
    Ensures only 1 document is processed at a time across the entire app
    to prevent pile-up and timeouts on the Ollama inference server.
    """
    logger.info("Background document processing worker started.")
    while True:
        try:
            doc = await DOCUMENT_QUEUE.get()
            logger.info(f"Worker dequeued document: {doc.ticker}")
            await AgentExecutionService.process_document(doc)
        except asyncio.CancelledError:
            logger.info("Background worker cancelled.")
            break
        except Exception as e:
            logger.error("AI Pipeline failed in worker", error=str(e))
        finally:
            DOCUMENT_QUEUE.task_done()


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

    docs_to_process = []

    for idx, res in enumerate(results):
        if isinstance(res, Exception):
            logger.error(f"Scraper {scrapers[idx].source_name} failed with exception: {res}")
        elif isinstance(res, list):
            logger.info(f"Scraper {scrapers[idx].source_name} scraped {len(res)} documents.")
            total_docs += len(res)
            
            # Filter by WITA "today"
            for doc in res:
                try:
                    doc_date_wita = doc.publication_date.astimezone(wita_tz).date()
                    if doc_date_wita >= today_wita:
                        docs_to_process.append(doc)
                except Exception as e:
                    logger.warning(f"Failed to parse date for {doc.ticker}: {e}")

    if docs_to_process:
        logger.info(f"Enqueueing {len(docs_to_process)} documents for background AI processing.")
        for doc in docs_to_process:
            DOCUMENT_QUEUE.put_nowait(doc)
        
    logger.info(f"Finished scraping cycle. Total documents fetched: {total_docs}")

# Global scheduler instance
scheduler = AsyncIOScheduler()

async def log_heartbeat():
    logger.info(f"System heartbeat: Idle and waiting for next scrape... Queue size: {DOCUMENT_QUEUE.qsize()}")

scheduler.add_job(log_heartbeat, 'interval', minutes=1)
scheduler.add_job(run_all_scrapers, 'cron', minute='*/5')
