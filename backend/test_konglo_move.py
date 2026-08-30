import asyncio
import os
import sys
from datetime import datetime, timezone

from app.services.agent import AgentExecutionService
from app.schemas.event_schema import ScrapedRawDocument

async def main():
    print("=== SCENARIO 1: TEXT ONLY (e.g. Google News / CNBC) ===")
    event1 = ScrapedRawDocument(
        ticker="GOTO",
        title="Grup Salim Borong Saham GOTO Rp 1 Triliun di Pasar Nego",
        source_url="http://test.com/konglo-text",
        publication_date=datetime.now(timezone.utc),
        raw_text="""
        Jakarta - Muncul pergerakan masif pada saham PT GoTo Gojek Tokopedia Tbk (GOTO). 
        Dikabarkan bahwa Anthony Salim melalui entitas usahanya memborong saham GOTO senilai lebih dari Rp 1 Triliun.
        Transaksi crossing jumbo ini terjadi di pasar negosiasi pada sesi pertama perdagangan hari ini.
        Ini adalah indikasi akumulasi besar-besaran oleh konglomerat ternama Indonesia.
        """,
        source_name="CNBC_RSS"
    )
    
    print("Processing Scenario 1...")
    res1 = await AgentExecutionService.process_document(event1)
    print(f"Scenario 1 Category: {res1.get('category')}")
    print("-" * 50)
    
    print("=== SCENARIO 2: WITH PDF TEXT (e.g. IDX Announcement) ===")
    event2 = ScrapedRawDocument(
        ticker="BREN",
        title="Keterbukaan Informasi: Pengambilalihan Saham Pengendali",
        source_url="http://test.com/konglo-pdf",
        publication_date=datetime.now(timezone.utc),
        raw_text="""
        KETERBUKAAN INFORMASI
        Tujuan: Memenuhi Peraturan OJK tentang Pengambilalihan
        
        Dengan ini kami sampaikan bahwa telah terjadi perubahan Pemegang Saham Pengendali (PSP) 
        di tubuh perseroan, di mana PT Barito Pacific (Prajogo Pangestu) melakukan pengambilalihan 
        saham secara masif sebanyak 20% kepemilikan. 
        Nilai transaksi mencapai Rp 5 Triliun. 
        Tender offer wajib (MTO) akan segera dilaksanakan menyusul pengambilalihan ini.
        """,
        source_name="IDX_ANNOUNCEMENT"
    )
    
    print("Processing Scenario 2...")
    res2 = await AgentExecutionService.process_document(event2)
    print(f"Scenario 2 Category: {res2.get('category')}")
    print("=== DONE ===")

if __name__ == "__main__":
    asyncio.run(main())
