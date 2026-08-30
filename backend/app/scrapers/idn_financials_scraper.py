from datetime import datetime, timezone
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas.event_schema import ScrapedRawDocument
from app.scrapers.base_scraper import BaseScraper
from app.utils.logger import get_logger

logger = get_logger("scraper.idn_financials")


class IDNFinancialsScraper(BaseScraper):
    """
    Scraper for IDN Financials Corporate Actions (structured HTML tables).
    """

    TARGET_URL = "https://www.idnfinancials.com/id/corporate-actions"

    def __init__(self):
        super().__init__(source_name="IDN_FINANCIALS")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_html(self) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.TARGET_URL, wait_until="domcontentloaded")
            html = await page.content()
            await browser.close()
            return html

    def _extract_ticker(self, text: str) -> str:
        match_idx = re.search(r"\b([A-Z]{4})\b", text)
        if match_idx and match_idx.group(1) not in {"IDR", "USD", "RUPS", "BANK", "BEI", "IDX", "PT"}:
            return match_idx.group(1)
        return "UNKNOWN"

    async def scrape(self) -> list[ScrapedRawDocument]:
        documents: list[ScrapedRawDocument] = []
        try:
            html = await self._fetch_html()
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select("table.table tr")[1:15]
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cols) >= 3:
                    ticker = self._extract_ticker(cols[0])
                    title = f"Corporate Action {ticker}: {cols[1]} - {cols[2]}"
                    doc = ScrapedRawDocument(
                        ticker=ticker,
                        title=title,
                        source_url=self.TARGET_URL,
                        publication_date=datetime.now(timezone.utc),
                        raw_text=f"{title}\nDetails: {' | '.join(cols)}",
                        source_name=self.source_name,
                    )
                    documents.append(doc)
        except Exception as e:
            logger.error("Failed to scrape IDN Financials", error=str(e))
        self.save_to_cache(documents)
        return documents
