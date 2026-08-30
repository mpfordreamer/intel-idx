import pytest
import asyncio
from typing import List

from app.scrapers.idx_announcement_scraper import IDXAnnouncementScraper
from app.scrapers.google_news_rss_scraper import GoogleNewsRSSScraper
from app.scrapers.cnbc_rss_scraper import CNBCRSSScraper
from app.scrapers.kontan_rss_scraper import KontanRSSScraper
from app.scrapers.idn_financials_scraper import IDNFinancialsScraper
from app.scrapers.ipotnews_scraper import IPOTNewsScraper
from app.schemas.event_schema import ScrapedRawDocument

@pytest.mark.asyncio
async def test_idx_announcement_scraper_live():
    scraper = IDXAnnouncementScraper()
    docs = await scraper.scrape()
    assert isinstance(docs, list), "Should return a list"
    if len(docs) > 0:
        doc = docs[0]
        assert isinstance(doc, ScrapedRawDocument)
        print(f"\n[IDX] Scraped {len(docs)} documents. Sample: {doc.title} ({doc.ticker})")
    else:
        print("\n[IDX] No documents found currently.")

@pytest.mark.asyncio
async def test_google_news_rss_scraper_live():
    scraper = GoogleNewsRSSScraper()
    docs = await scraper.scrape()
    assert isinstance(docs, list)
    if len(docs) > 0:
        doc = docs[0]
        assert isinstance(doc, ScrapedRawDocument)
        print(f"\n[Google News] Scraped {len(docs)} documents. Sample: {doc.title} ({doc.ticker})")
    else:
        print("\n[Google News] No documents found currently.")

@pytest.mark.asyncio
async def test_cnbc_rss_scraper_live():
    scraper = CNBCRSSScraper()
    docs = await scraper.scrape()
    assert isinstance(docs, list)
    if len(docs) > 0:
        doc = docs[0]
        assert isinstance(doc, ScrapedRawDocument)
        print(f"\n[CNBC] Scraped {len(docs)} documents. Sample: {doc.title} ({doc.ticker})")
    else:
        print("\n[CNBC] No documents found currently.")

@pytest.mark.asyncio
async def test_kontan_rss_scraper_live():
    scraper = KontanRSSScraper()
    docs = await scraper.scrape()
    assert isinstance(docs, list)
    if len(docs) > 0:
        doc = docs[0]
        assert isinstance(doc, ScrapedRawDocument)
        print(f"\n[Kontan] Scraped {len(docs)} documents. Sample: {doc.title} ({doc.ticker})")
    else:
        print("\n[Kontan] No documents found currently.")

@pytest.mark.skip(reason="Temporarily disabled per implementation plan")
@pytest.mark.asyncio
async def test_idn_financials_scraper_live():
    scraper = IDNFinancialsScraper()
    docs = await scraper.scrape()
    assert isinstance(docs, list)
    if len(docs) > 0:
        doc = docs[0]
        assert isinstance(doc, ScrapedRawDocument)
        print(f"\n[IDN Financials] Scraped {len(docs)} documents. Sample: {doc.title} ({doc.ticker})")
    else:
        print("\n[IDN Financials] No documents found currently.")

@pytest.mark.skip(reason="Temporarily disabled per implementation plan")
@pytest.mark.asyncio
async def test_ipotnews_scraper_live():
    scraper = IPOTNewsScraper()
    docs = await scraper.scrape()
    assert isinstance(docs, list)
    if len(docs) > 0:
        doc = docs[0]
        assert isinstance(doc, ScrapedRawDocument)
        print(f"\n[IPOTNews] Scraped {len(docs)} documents. Sample: {doc.title} ({doc.ticker})")
    else:
        print("\n[IPOTNews] No documents found currently.")
