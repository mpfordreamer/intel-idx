import asyncio
from datetime import datetime, timezone
import re
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas.event_schema import ScrapedRawDocument
from app.scrapers.base_scraper import BaseScraper
from app.utils.logger import get_logger

logger = get_logger("scraper.tradingview_news")


class TradingViewNewsScraper(BaseScraper):
    """
    Scraper for TradingView real-time financial headlines feed.
    Aggregates multi-market news (IDX, S&P 500, Commodities: Gold, Silver, Tin, Aluminium, Oil, etc.).
    Fast, real-time, non-blocking, and free of CAPTCHA.
    """

    HEADLINES_ENDPOINT_EN = "https://news-headlines.tradingview.com/v2/headlines?client=web&lang=en"

    def __init__(self):
        super().__init__(source_name="TRADINGVIEW_REALTIME")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_headlines(self, url: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    def _extract_ticker_and_symbols(self, item: dict[str, Any]) -> tuple[str, list[str]]:
        """
        Extracts primary US/Global ticker and related symbols from TradingView payload.
        Handles US equities (NASDAQ, NYSE, AMEX), US-listed ETFs, and global commodities.
        Strictly excludes Indonesian / IDX domestic tickers.
        """
        symbols = []
        related = item.get("relatedSymbols", [])
        if isinstance(related, list):
            for s in related:
                sym = s.get("symbol", "")
                if sym and not sym.startswith("IDX:"):
                    symbols.append(sym)

        # 1. Check title for $TICKER (1-5 chars for US stocks / ETFs)
        title = item.get("title", "")
        match_dollar = re.search(r"\$([A-Z]{1,5})\b", title)
        if match_dollar:
            return match_dollar.group(1).upper(), symbols

        # 2. Check for US exchange prefixes in symbols (e.g. NASDAQ:AAPL, NYSE:NVDA)
        for sym in symbols:
            parts = sym.split(":")
            if len(parts) == 2 and parts[0] in {"NASDAQ", "NYSE", "AMEX", "CBOE", "COMEX", "NYMEX", "LME"}:
                return parts[1].upper(), symbols

        # 3. Check for foreign/commodity symbols in relatedSymbols
        if symbols:
            first_sym = symbols[0].split(":")[-1]
            return first_sym.upper(), symbols

        return "GLOBAL_MACRO", symbols

    def _parse_items(self, data: dict[str, Any], max_items: int = 50, forced_ticker: str | None = None) -> list[ScrapedRawDocument]:
        documents: list[ScrapedRawDocument] = []
        items = data.get("items", [])
        for item in items[:max_items]:
            title = item.get("title", "").strip()
            if not title:
                continue

            story_path = item.get("storyPath", "")
            source_url = f"https://www.tradingview.com{story_path}" if story_path.startswith("/") else item.get("link", story_path)
            if not source_url:
                source_url = "https://www.tradingview.com/news/"

            pub_timestamp = item.get("published")
            if pub_timestamp:
                pub_date = datetime.fromtimestamp(pub_timestamp, tz=timezone.utc)
            else:
                pub_date = datetime.now(timezone.utc)

            source_provider = item.get("source", "TradingView")
            ticker, symbols = self._extract_ticker_and_symbols(item)

            if forced_ticker:
                search_text = f"{title} {' '.join(symbols)}".lower()
                if forced_ticker.lower() not in search_text and ticker != forced_ticker:
                    continue
                ticker = forced_ticker

            sym_str = ", ".join(symbols) if symbols else "General Market"
            raw_text = f"{title}\n\nPenerbit: {source_provider}\nSimbol Terkait: {sym_str}"

            doc = ScrapedRawDocument(
                ticker=ticker,
                title=title,
                source_url=source_url,
                publication_date=pub_date,
                raw_text=raw_text,
                source_name=self.source_name,
            )
            documents.append(doc)
        return documents

    async def scrape(self) -> list[ScrapedRawDocument]:
        """
        Fetches real-time US and Global financial market headlines.
        Standardizes to ScrapedRawDocument DTOs. Strictly excludes Indonesian local feeds.
        """
        documents: list[ScrapedRawDocument] = []
        try:
            res_en = await self._fetch_headlines(self.HEADLINES_ENDPOINT_EN)
            if isinstance(res_en, dict):
                documents.extend(self._parse_items(res_en, max_items=50))
        except Exception as e:
            logger.error("Failed to scrape TradingView US headlines", error=str(e))

        # Deduplicate documents in memory by title
        seen_titles = set()
        unique_docs: list[ScrapedRawDocument] = []
        for doc in documents:
            if doc.title not in seen_titles:
                seen_titles.add(doc.title)
                unique_docs.append(doc)

        self.save_to_cache(unique_docs)
        return unique_docs

    async def scrape_by_ticker(self, ticker: str) -> list[ScrapedRawDocument]:
        """On-demand scrape for a specific stock ticker."""
        all_docs = await self.scrape()
        return [d for d in all_docs if d.ticker.upper() == ticker.upper() or ticker.lower() in d.title.lower()]
