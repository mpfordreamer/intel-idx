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

logger = get_logger("scraper.kontan_rss")


class KontanRSSScraper(BaseScraper):
    """
    Scraper for Kontan Investasi RSS Feed (detailed quantitative corporate actions: Right Issue, Stock Split, Private Placement, Warrant).
    """

    RSS_ENDPOINT = "https://investasi.kontan.co.id/rss"

    def __init__(self):
        super().__init__(source_name="KONTAN_INVESTASI_RSS")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_rss(self) -> Any:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            response = await client.get(self.RSS_ENDPOINT, headers=headers)
            response.raise_for_status()
            return await asyncio.to_thread(feedparser.parse, response.text)

    def _extract_ticker(self, text: str) -> str:
        match_dollar = re.search(r"\$([A-Z]{4})\b", text)
        if match_dollar:
            return match_dollar.group(1)
        match_idx = re.search(r"\b([A-Z]{4})\s*(?:Tbk|saham|emiten)?\b", text)
        if match_idx and match_idx.group(1) not in {"IDR", "USD", "RUPS", "BANK", "BEI", "IDX", "PT"}:
            return match_idx.group(1)
        return "UNKNOWN"

    async def scrape(self) -> list[ScrapedRawDocument]:
        documents: list[ScrapedRawDocument] = []
        try:
            feed = await self._fetch_rss()
            for entry in feed.entries[:25]:
                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "")
                summary_html = getattr(entry, "summary", "")
                summary = BeautifulSoup(summary_html, "html.parser").get_text().strip()

                ticker = self._extract_ticker(f"{title} {summary}")

                published_parsed = getattr(entry, "published_parsed", None)
                if published_parsed:
                    pub_date = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                else:
                    pub_date = datetime.now(timezone.utc)

                doc = ScrapedRawDocument(
                    ticker=ticker,
                    title=title,
                    source_url=link,
                    publication_date=pub_date,
                    raw_text=f"{title}\n\n{summary}",
                    source_name=self.source_name,
                )
                documents.append(doc)
        except Exception as e:
            logger.error("Failed to scrape Kontan Investasi RSS", error=str(e))
        self.save_to_cache(documents)
        return documents
