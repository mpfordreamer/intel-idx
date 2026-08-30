import os
import httpx
import pdfplumber
from datetime import datetime, timezone
import json
import random
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas.event_schema import ScrapedRawDocument
from app.scrapers.base_scraper import BaseScraper
from app.utils.logger import get_logger

logger = get_logger("scraper.idx")


class IDXAnnouncementScraper(BaseScraper):
    """
    Scraper for official IDX / BEI corporate announcements (Keterbukaan Informasi) 
    and general IDX News (Berita / Pengumuman).
    """

    IDX_ANNOUNCEMENT_API_URL = "https://idx.co.id/primary/ListedCompany/GetAnnouncement"
    IDX_NEWS_API_URL = "https://idx.co.id/primary/NewsAnnouncement/GetNewsSearch"

    def __init__(self):
        super().__init__(source_name="BEI_OFFICIAL")

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extracts text from a locally saved PDF using pdfplumber."""
        extracted_text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
            return extracted_text.strip()
        except Exception as e:
            logger.error(f"Failed to extract PDF {file_path}", error=str(e))
            return ""

    def _cleanup_pdf_cache(self, max_files: int = 200):
        """Removes oldest PDF files to keep the cache size within max_files limit."""
        pdf_cache_dir = os.path.join(self.cache_dir, "pdfs")
        if not os.path.exists(pdf_cache_dir):
            return

        try:
            # Get all .pdf files with their full paths
            files = [os.path.join(pdf_cache_dir, f) for f in os.listdir(pdf_cache_dir) if f.lower().endswith('.pdf')]
            
            # If the number of files exceeds the limit
            if len(files) > max_files:
                # Sort files by modification time (oldest first)
                files.sort(key=os.path.getmtime)
                
                # Number of files to delete
                files_to_delete = len(files) - max_files
                
                for i in range(files_to_delete):
                    try:
                        os.remove(files[i])
                        logger.info(f"Deleted old PDF cache file: {files[i]}")
                    except Exception as e:
                        logger.error(f"Failed to delete old PDF {files[i]}", error=str(e))
                
                logger.info(f"Cleaned up {files_to_delete} old PDFs. Cache is now at {max_files} files.")
        except Exception as e:
            logger.error("Error during PDF cache cleanup", error=str(e))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_announcements(self) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                accept_downloads=True
            )
            page = await context.new_page()
            
            try:
                # 1. Visit main page to get cookies and solve potential JS challenges
                await page.goto("https://idx.co.id/id", wait_until="networkidle")
                await page.wait_for_timeout(random.randint(1500, 4500))
                
                # 2. Visit keterbukaan informasi page to set Referer context
                await page.goto("https://idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi", wait_until="networkidle")
                await page.wait_for_timeout(random.randint(1500, 4500))

                # 3. Hit the API endpoint with pageSize=25
                url = f"{self.IDX_ANNOUNCEMENT_API_URL}?indexFrom=0&pageSize=25"
                response = await page.goto(url, wait_until="domcontentloaded")
                
                text = await page.inner_text("body")
                data = json.loads(text)

                # 4. Use the same safe context to download PDFs immediately
                for item in data.get("Replies", []):
                    attachments = item.get("attachments", [])
                    if len(attachments) > 0 and attachments[0].get("FullSavePath"):
                        pdf_url = attachments[0].get("FullSavePath")
                        if pdf_url.lower().endswith(".pdf"):
                            try:
                                pdf_url = pdf_url.replace("www.idx.co.id", "idx.co.id")
                                
                                pdf_page = await context.new_page()
                                try:
                                    async with pdf_page.expect_download(timeout=10000) as download_info:
                                        try:
                                            await pdf_page.goto(
                                                pdf_url,
                                                referer="https://idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi"
                                            )
                                        except Exception:
                                            pass
                                    download = await download_info.value
                                    
                                    import uuid
                                    pdf_cache_dir = os.path.join(self.cache_dir, "pdfs")
                                    os.makedirs(pdf_cache_dir, exist_ok=True)
                                    pdf_id = item.get('Id') or uuid.uuid4().hex
                                    pdf_path = os.path.join(pdf_cache_dir, f"{pdf_id}.pdf")
                                    
                                    await download.save_as(pdf_path)
                                        
                                    item["_downloaded_pdf_path"] = pdf_path
                                    logger.info(f"Successfully saved PDF to {pdf_path}")
                                except Exception as e:
                                    logger.warning(f"Exception downloading PDF {pdf_url}: {e}")
                                finally:
                                    await pdf_page.close()
                            except Exception as e:
                                logger.error(f"Error downloading PDF in context: {e}")
            finally:
                await browser.close()

            return data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_news(self) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            try:
                await page.goto("https://idx.co.id/id", wait_until="networkidle")
                await page.wait_for_timeout(random.randint(1500, 4500))
                
                await page.goto("https://idx.co.id/id/berita/pengumuman", wait_until="networkidle")
                await page.wait_for_timeout(random.randint(1500, 4500))

                url = f"{self.IDX_NEWS_API_URL}?pageNumber=1&pageSize=25&locale=id-id"
                response = await page.goto(url, wait_until="domcontentloaded")
                
                text = await page.inner_text("body")
                data = json.loads(text)
            finally:
                await browser.close()

            return data

    async def scrape(self) -> list[ScrapedRawDocument]:
        documents: list[ScrapedRawDocument] = []
        
        # 1. Scrape Keterbukaan Informasi
        try:
            data = await self._fetch_announcements()
            items = data.get("Replies", [])
            for item in items:
                pengumuman = item.get("pengumuman", {})
                attachments = item.get("attachments", [])
                
                ticker = str(pengumuman.get("Kode_Emiten", "UNKNOWN")).strip().upper()
                title = str(pengumuman.get("JudulPengumuman", "")).strip()
                summary = str(pengumuman.get("PerihalPengumuman", title)).strip()
                
                url = "https://idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi"
                pdf_text = ""
                
                if len(attachments) > 0 and attachments[0].get("FullSavePath"):
                    url = attachments[0].get("FullSavePath")
                    
                downloaded_pdf_path = item.get("_downloaded_pdf_path")
                if downloaded_pdf_path:
                    pdf_text = self._extract_pdf_text(downloaded_pdf_path)

                pub_time_str = pengumuman.get("TglPengumuman")
                try:
                    pub_date = datetime.fromisoformat(str(pub_time_str)).astimezone(timezone.utc)
                except Exception:
                    pub_date = datetime.now(timezone.utc)
                    
                raw_text = f"{title}\n\n{summary}"
                if pdf_text:
                    raw_text += f"\n\n--- Isi Lampiran PDF ---\n{pdf_text}"

                doc = ScrapedRawDocument(
                    ticker=ticker,
                    title=f"[Announcements] {title}",
                    source_url=url,
                    publication_date=pub_date,
                    raw_text=raw_text,
                    source_name=self.source_name,
                )
                documents.append(doc)
        except Exception as e:
            logger.error("Failed to scrape IDX announcements", error=str(e))
            
        # 2. Scrape Berita / Pengumuman
        # try:
        #     news_data = await self._fetch_news()
        #     news_items = news_data.get("Items", [])
        #     for item in news_items:
        #         title = str(item.get("Title", "")).strip()
        #         summary = str(item.get("Summary", title)).strip()
        #         news_id = item.get("Id", "")
        #         
        #         url = f"https://www.idx.co.id/id/berita/pengumuman/{news_id}" if news_id else "https://www.idx.co.id/id/berita/pengumuman"
        #
        #         pub_time_str = item.get("PublishedDate")
        #         try:
        #             pub_date = datetime.fromisoformat(str(pub_time_str)).astimezone(timezone.utc)
        #         except Exception:
        #             pub_date = datetime.now(timezone.utc)
        #
        #         doc = ScrapedRawDocument(
        #             ticker="IDX",  # General news usually doesn't belong to one ticker
        #             title=f"[News] {title}",
        #             source_url=url,
        #             publication_date=pub_date,
        #             raw_text=f"{title}\n{summary}",
        #             source_name=self.source_name,
        #         )
        #         documents.append(doc)
        # except Exception as e:
        #     logger.error("Failed to scrape IDX news", error=str(e))

        self._cleanup_pdf_cache(max_files=200)
        self.save_to_cache(documents)
        return documents
