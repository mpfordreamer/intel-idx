import asyncio
from datetime import datetime, timezone
import re
from typing import Any
import feedparser
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas.event_schema import ScrapedRawDocument
from app.scrapers.base_scraper import BaseScraper
from app.utils.logger import get_logger

logger = get_logger("scraper.cnbc_global")


class CNBCGlobalScraper(BaseScraper):
    """
    Scraper for official CNBC International / US RSS Feeds.
    Covers Wall Street Markets, Tech & NASDAQ, Economy & The Fed, and Investing / S&P 500.
    Caches historical documents to backend/cache/cnbc_global_history.jsonl.
    """

    RSS_ENDPOINTS = [
        ("Wall Street Markets", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
        ("Tech and NASDAQ", "https://www.cnbc.com/id/19854910/device/rss/rss.html"),
        ("Economy and The Fed", "https://www.cnbc.com/id/10000115/device/rss/rss.html"),
        ("Investing and SP500", "https://www.cnbc.com/id/15839069/device/rss/rss.html"),
    ]

    def __init__(self):
        super().__init__(source_name="CNBC_GLOBAL")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_rss(self, url: str) -> Any:
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return await asyncio.to_thread(feedparser.parse, response.text)

    def _extract_us_ticker(self, text: str) -> str:
        """
        Extracts prominent US stock and ETF tickers from title and description.
        Prioritizes $TICKER format, then known mega-tech, S&P 500, and ETF symbols.
        """
        match_dollar = re.search(r"\$([A-Z]{1,5})\b", text)
        if match_dollar:
            return match_dollar.group(1).upper()

        common_us_tickers = [
            "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "META", "TSLA",
            "AVGO", "AMD", "INTC", "QCOM", "ASML", "TSM", "ARM", "MU",
            "JPM", "BAC", "WFC", "GS", "MS", "C", "BRK", "V", "MA",
            "XOM", "CVX", "COP", "LMT", "RTX", "BA", "CAT", "GE",
            "LLY", "UNH", "PFE", "JNJ",
            "SPY", "VOO", "QQQ", "DIA", "IWM", "XLK", "SMH", "SOXX", "XLF", "XLE", "TLT", "UUP", "GLD", "SLV", "USO",
        ]
        for t in common_us_tickers:
            if re.search(r"\b" + re.escape(t) + r"\b", text):
                return t

        return "GLOBAL_MACRO"

    def _parse_feed(self, feed: Any, max_items: int = 15) -> list[ScrapedRawDocument]:
        documents: list[ScrapedRawDocument] = []
        for entry in getattr(feed, "entries", [])[:max_items]:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "")
            summary_html = getattr(entry, "summary", "")
            summary = BeautifulSoup(summary_html, "html.parser").get_text().strip()

            if not title or not link:
                continue

            pub_parsed = getattr(entry, "published_parsed", None)
            if pub_parsed:
                pub_date = datetime(*pub_parsed[:6], tzinfo=timezone.utc)
            else:
                pub_date = datetime.now(timezone.utc)

            ticker = self._extract_us_ticker(f"{title} {summary}")
            raw_text = f"{title}\n\n{summary}\n\nSumber: CNBC Global (US Markets & Macro)"

            doc = ScrapedRawDocument(
                ticker=ticker,
                title=title,
                source_url=link,
                publication_date=pub_date,
                raw_text=raw_text,
                source_name=self.source_name,
            )
            documents.append(doc)
        return documents

    async def scrape(self) -> list[ScrapedRawDocument]:
        """
        Scrapes concurrent feeds across official CNBC Markets, Tech/NASDAQ, Economy/Fed, and Investing.
        Deduplicates by title and persists to backend/cache/cnbc_global_history.jsonl.
        """
        all_docs: list[ScrapedRawDocument] = []
        try:
            tasks = [self._fetch_rss(url) for _, url in self.RSS_ENDPOINTS]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if not isinstance(res, Exception) and hasattr(res, "entries"):
                    all_docs.extend(self._parse_feed(res))
                elif isinstance(res, Exception):
                    logger.warning(f"CNBC Global RSS feed fetch failed: {res}")

        except Exception as e:
            logger.error("Failed to scrape CNBC Global feeds", error=str(e))

        seen_titles = set()
        unique_docs: list[ScrapedRawDocument] = []
        for doc in all_docs:
            norm_title = re.sub(r"[^\w\s]", "", doc.title.lower()).strip()
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique_docs.append(doc)

        self.save_to_cache(unique_docs)
        logger.info(f"CNBC Global scrape completed: {len(unique_docs)} unique articles cached")
        return unique_docs
