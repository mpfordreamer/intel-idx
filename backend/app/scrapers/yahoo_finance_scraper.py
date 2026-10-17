import asyncio
from datetime import datetime, timezone
import re
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas.event_schema import ScrapedRawDocument
from app.scrapers.base_scraper import BaseScraper
from app.utils.logger import get_logger

logger = get_logger("scraper.yahoo_finance")


class DynamicQueryManager:
    """Manages modular, flexible, and adaptive search queries across US Equities, Macro, and Commodities."""

    EQUITY_QUERIES = [
        "SPY",
        "NASDAQ",
        "Semiconductor",
        "Stocks",
    ]

    MACRO_QUERIES = [
        "CPI",
        "Inflation",
        "Fed",
        "Kevin Warsh",
        "Trump",
        "Treasury Yield",
        "DXY",
    ]

    COMMODITY_QUERIES = [
        "Gold",
        "Silver",
        "Copper",
        "Aluminum",
        "Nickel",
        "Tin",
        "Coal",
        "CPO",
        "Crude Oil",
        "Natural Gas",
        "Commodities",
    ]

    @classmethod
    def get_active_queries(cls, topic: str | None = None) -> list[str]:
        if topic == "macro":
            return cls.MACRO_QUERIES
        if topic == "equities":
            return cls.EQUITY_QUERIES
        if topic == "commodities":
            return cls.COMMODITY_QUERIES
        return cls.EQUITY_QUERIES + cls.MACRO_QUERIES + cls.COMMODITY_QUERIES


class YahooFinanceScraper(BaseScraper):
    """
    Scraper for Yahoo Finance real-time news search and feeds.
    Provides structured global macroeconomic, S&P 500, NASDAQ, and expanded commodity coverage.
    Free, high speed, structured JSON responses. Strictly isolated from IDX domestic news.
    """

    SEARCH_ENDPOINT = "https://query2.finance.yahoo.com/v1/finance/search"

    def __init__(self):
        super().__init__(source_name="YAHOO_FINANCE_REALTIME")

    @property
    def SEARCH_QUERIES(self) -> list[str]:
        return DynamicQueryManager.get_active_queries()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_search(self, query: str, client: httpx.AsyncClient) -> dict[str, Any]:
        params = {
            "q": query,
            "quotesCount": 0,
            "newsCount": 15,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        response = await client.get(self.SEARCH_ENDPOINT, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def _extract_ticker(self, title: str, related_tickers: list[str]) -> str:
        # 1. Check title for $TICKER (1-5 chars for US stocks / ETFs)
        match = re.search(r"\$([A-Z]{1,5})\b", title)
        if match:
            return match.group(1).upper()

        # 2. Check related_tickers for US/Global symbols (strictly ignore .JK / Indonesian tickers)
        for t in related_tickers:
            if not t.endswith(".JK") and not t.endswith(".ID"):
                return t.upper()

        return "GLOBAL_MACRO"

    def _parse_news(self, data: dict[str, Any], forced_ticker: str | None = None) -> list[ScrapedRawDocument]:
        documents: list[ScrapedRawDocument] = []
        news_items = data.get("news", [])
        for item in news_items:
            title = item.get("title", "").strip()
            link = item.get("link", "")
            if not title or not link:
                continue

            pub_timestamp = item.get("providerPublishTime")
            if pub_timestamp:
                pub_date = datetime.fromtimestamp(pub_timestamp, tz=timezone.utc)
            else:
                pub_date = datetime.now(timezone.utc)

            publisher = item.get("publisher", "Yahoo Finance")
            related = item.get("relatedTickers", [])
            ticker = self._extract_ticker(title, related)

            if forced_ticker:
                search_text = f"{title} {' '.join(related)}".lower()
                if forced_ticker.lower() not in search_text and ticker != forced_ticker:
                    continue
                ticker = forced_ticker

            related_str = ", ".join(related) if related else "Macro / Commodity"
            raw_text = f"{title}\n\nPenerbit: {publisher}\nSimbol Terkait: {related_str}"

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
        Executes concurrent searches across strategic Indonesian, S&P 500, and commodity queries.
        Returns deduplicated ScrapedRawDocument list.
        """
        all_docs: list[ScrapedRawDocument] = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                tasks = [self._fetch_search(q, client) for q in self.SEARCH_QUERIES]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for res in results:
                    if isinstance(res, dict):
                        all_docs.extend(self._parse_news(res))
                    elif isinstance(res, Exception):
                        logger.warning(f"Yahoo Finance search task failed: {res}")

        except Exception as e:
            logger.error("Failed to scrape Yahoo Finance", error=str(e))

        # Deduplicate by URL or Title
        seen_titles = set()
        unique_docs: list[ScrapedRawDocument] = []
        for doc in all_docs:
            if doc.title not in seen_titles:
                seen_titles.add(doc.title)
                unique_docs.append(doc)

        self.save_to_cache(unique_docs)
        return unique_docs

    async def scrape_by_ticker(self, ticker: str) -> list[ScrapedRawDocument]:
        """Targeted scrape for a specific symbol or topic."""
        query = ticker
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                data = await self._fetch_search(query, client)
                return self._parse_news(data, forced_ticker=ticker)
        except Exception as e:
            logger.error(f"Yahoo Finance scrape_by_ticker failed for {ticker}", error=str(e))
            return []
