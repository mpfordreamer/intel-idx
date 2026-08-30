import pytest
from datetime import datetime, timezone
from app.schemas.event_schema import ScrapedRawDocument


@pytest.fixture
def sample_backdoor_document() -> ScrapedRawDocument:
    return ScrapedRawDocument(
        ticker="BUMI",
        title="BUMI Siap Lakukan Backdoor Listing dan Injeksi Aset Baru",
        source_url="https://idx.co.id/announcements/1",
        publication_date=datetime(2026, 7, 26, 10, 0, tzinfo=timezone.utc),
        raw_text="PT Bumi Resources Tbk bersiap melakukan backdoor listing melalui injeksi aset baru ke perusahaan cangkang.",
        source_name="BEI_OFFICIAL",
    )


@pytest.fixture
def sample_konglo_document() -> ScrapedRawDocument:
    return ScrapedRawDocument(
        ticker="BUMI",
        title="Grup Salim Mach Energy Masuk BUMI Rp 24 Triliun",
        source_url="https://cnbcindonesia.com/news/1",
        publication_date=datetime(2026, 7, 26, 11, 0, tzinfo=timezone.utc),
        raw_text="Grup Salim melalui Mach Energy melakukan crossing pasar negosiasi saham BUMI senilai Rp 24 Triliun.",
        source_name="CNBC_MARKET_RSS",
    )


@pytest.fixture
def sample_irrelevant_document() -> ScrapedRawDocument:
    return ScrapedRawDocument(
        ticker="ASII",
        title="Jadwal Pembagian Dividen Tunai Astra International ASII",
        source_url="https://kontan.co.id/news/1",
        publication_date=datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc),
        raw_text="PT Astra International Tbk mengumumkan jadwal pembagian dividen tunai tahun buku 2025.",
        source_name="KONTAN_INVESTASI_RSS",
    )
