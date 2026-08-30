import os
import json
from abc import ABC, abstractmethod
from app.schemas.event_schema import ScrapedRawDocument


class BaseScraper(ABC):
    """
    Abstract base scraper class following Open/Closed Principle (OCP).
    New data sources can be integrated by implementing this async interface.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def save_to_cache(self, documents: list[ScrapedRawDocument]):
        """
        Saves scraped documents to a JSON Lines history file for debugging/cache.
        """
        if not documents:
            return
        
        file_path = os.path.join(self.cache_dir, f"{self.source_name.lower()}_history.jsonl")
        
        with open(file_path, "a", encoding="utf-8") as f:
            for doc in documents:
                doc_dict = doc.model_dump(mode="json")
                f.write(json.dumps(doc_dict, ensure_ascii=False) + "\n")


    @abstractmethod
    async def scrape(self) -> list[ScrapedRawDocument]:
        """
        Asynchronously fetches and parses documents from target source.
        Returns a list of standardized ScrapedRawDocument DTOs.
        """
        pass
