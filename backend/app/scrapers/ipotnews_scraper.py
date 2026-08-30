from datetime import datetime, timezone
import re
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas.event_schema import ScrapedRawDocument
from app.scrapers.base_scraper import BaseScraper
from app.utils.logger import get_logger

logger = get_logger("scraper.ipotnews")


class IPOTNewsScraper(BaseScraper):
    """
    Scraper for IPOTNews Corporate Actions & Market Moves.
    """

    TARGET_URL = "https://www.indopremier.com/ipotnews/"

    def __init__(self):
        super().__init__(source_name="IPOT_NEWS")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_html(self) -> str:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            response = await client.get(self.TARGET_URL, headers=headers)
            response.raise_for_status()
            return response.text

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
            html = await self._fetch_html()
            soup = BeautifulSoup(html, "html.parser")
            news_items = soup.select("div.media-body")[:15]
            for item in news_items:
                title_elem = item.find("h5") or item.find("a")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                link_elem = item.find("a", href=True)
                link = link_elem["href"] if link_elem else self.TARGET_URL
                if link and not link.startswith("http"):
                    link = f"https://www.indopremier.com/ipotnews/{link}"

                summary = item.get_text(strip=True)
                ticker = self._extract_ticker(f"{title} {summary}")

                doc = ScrapedRawDocument(
                    ticker=ticker,
                    title=title,
                    source_url=link,
                    publication_date=datetime.now(timezone.utc),
                    raw_text=f"{title}\n\n{summary}",
                    source_name=self.source_name,
                )
                documents.append(doc)
        except Exception as e:
            logger.error("Failed to scrape IPOTNews", error=str(e))
        self.save_to_cache(documents)
        return documents
