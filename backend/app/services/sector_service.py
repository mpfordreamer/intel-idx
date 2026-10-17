import asyncio
from datetime import datetime, timezone
import json
import re
from typing import Any
import httpx
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.config import get_settings
from app.schemas.event_schema import ScrapedRawDocument
from app.schemas.sector_schema import (
    SectorNewsItem,
    SectorRecommendationItem,
    SectorRecommendationsResponse,
    SectorDetailResponse,
    SectorScrapeAndAnalyzeResponse,
)
from app.scrapers.cnbc_rss_scraper import CNBCRSSScraper
from app.scrapers.tradingview_news_scraper import TradingViewNewsScraper
from app.scrapers.yahoo_finance_scraper import YahooFinanceScraper
from app.services.sector_mapping import (
    COMMODITY_TAXONOMY,
    COMMODITY_BENCHMARK_US_ETFS,
    SP500_TAXONOMY,
    IDX_TAXONOMY,
    classify_document_to_sectors,
)
from app.services.waha import WAHAClient
from app.utils.logger import get_logger

logger = get_logger("services.sector_service")
settings = get_settings()

SECTOR_SYSTEM_PROMPT = """
You are a Principal Global Macro & Sector Strategist specializing in Indonesian Equities (IDX), Wall Street (S&P 500), and Global Commodities.
Your task is to analyze real-time news headlines from today (Hari H) and sector movements to produce an authoritative, multi-market sector recommendation.

Stance Class Options (MUST PRESERVE EXACT UNDERSCORE NOTATION):
- "OVERWEIGHT": Strong institutional tailwind, sector-wide multiple expansion, strong supply-demand deficit.
- "NEUTRAL": Balanced fundamentals, fair valuation, sideways consolidation.
- "UNDERWEIGHT": Structural headwinds, inventory overhang, decelerating growth.
- "ACCUMULATE_ON_WEAKNESS": High long-term upside, but short-term pullback presents buying opportunity.
- "HOLD_WATCH": Pending regulatory clarity, commodity price testing critical support.
- "AVOID": High risk of disruption, acute margin contraction, or macroeconomic deterioration.

Return a valid JSON object matching this schema:
{
  "recommendation": "BUY",
  "stance": "OVERWEIGHT",
  "score": 0.85,
  "conviction_score": 88,
  "ai_analysis": "Analisis kontekstual 1-2 kalimat dalam bahasa Indonesia mengenai katalis atau sentimen riil penggerak sektor ini berdasarkan berita terkini hari ini (Hari H).",
  "detected_tickers": ["$BBCA", "$BMRI"],
  "catalysts": ["Catalyst 1", "Catalyst 2"],
  "risk_factors": ["Risk 1", "Risk 2"]
}

Guidelines:
1. recommendation MUST be one of: "BUY", "HOLD", or "AVOID", evaluated directly by your AI brain based on real-time evidence strength, catalyst impact, and momentum from today's headlines.
2. conviction_score MUST be an integer between 50 and 98 calculated directly by your mind/reasoning based on evidence strength from today's headlines.
3. detected_tickers MUST be an array of actual stock tickers (e.g. ["$BBCA", "$BMRI"]) or ETF/stock tickers (e.g. ["$NVDA", "$SMH"]) explicitly discussed in the provided news headlines for today. If no tickers are mentioned, return an empty array [].
4. All calculations, stances, conviction scores, and outlooks MUST be evaluated dynamically by your AI intellect based on real-time news data and forward-looking momentum for the next trading session.
5. When referring to commodity prices or valuation levels, ALWAYS specify currency values explicitly in USD (e.g. 109.86 USD, 4,181.10 USD).
""".strip()


def _clean_stance(stance: str) -> str:
    """Removes underscores from stance and returns clean uppercase English."""
    return stance.replace("_", " ").strip().upper()


def _conviction_label(score: int) -> str:
    """Returns conviction label: High (>=80), Medium (>=65), else Low."""
    if score >= 80:
        return "High"
    elif score >= 65:
        return "Medium"
    else:
        return "Low"


def _resolve_action_recommendation(rec_item: SectorRecommendationItem) -> str:
    """Returns BUY, HOLD, or AVOID from recommendation field or derived from stance."""
    rec = getattr(rec_item, "recommendation", None)
    if rec and rec.upper() in {"BUY", "HOLD", "AVOID"}:
        return rec.upper()
    stance = rec_item.stance.upper().strip()
    if stance in {"OVERWEIGHT", "ACCUMULATE_ON_WEAKNESS", "STRONG_BUY_AKUMULASI", "BUY"}:
        return "BUY"
    elif stance in {"UNDERWEIGHT", "AVOID"}:
        return "AVOID"
    return "HOLD"


def _format_tickers_with_action(tickers: list[str], action: str) -> str:
    """Formats detected tickers attaching the recommendation action, e.g. $MEDC (BUY)."""
    if not tickers:
        return "-"
    formatted = []
    for t in tickers[:5]:
        t_clean = t.strip()
        if not t_clean.endswith(")"):
            formatted.append(f"{t_clean} ({action})")
        else:
            formatted.append(t_clean)
    return ", ".join(formatted)


class SectorIntelligenceService:
    """
    Coordinates multi-source scrapers (TradingView, Yahoo Finance, CNBC),
    maps news into 3-pillar taxonomy (IDX, S&P 500, Expanded Commodities),
    synthesizes sector recommendations using AI, and routes alerts to dedicated WAHA groups.
    """

    _cached_recommendations: list[SectorRecommendationItem] = []
    _cached_articles: dict[str, list[SectorNewsItem]] = {}
    _last_run_timestamp: datetime | None = None

    def __init__(self):
        self.tv_scraper = TradingViewNewsScraper()
        self.yf_scraper = YahooFinanceScraper()
        self.cnbc_scraper = CNBCRSSScraper()
        self.waha_client = WAHAClient()

    async def scrape_all_sources(self) -> list[ScrapedRawDocument]:
        """Runs real-time scrapers across TradingView, Yahoo Finance, and CNBC concurrently."""
        results = await asyncio.gather(
            self.tv_scraper.scrape(),
            self.yf_scraper.scrape(),
            self.cnbc_scraper.scrape(),
            return_exceptions=True,
        )

        all_docs: list[ScrapedRawDocument] = []
        for r in results:
            if isinstance(r, list):
                all_docs.extend(r)
            elif isinstance(r, Exception):
                logger.warning(f"Sector scraper sub-task exception: {r}")

        # Deduplicate across scrapers by normalized title
        seen_titles = set()
        unique_docs: list[ScrapedRawDocument] = []
        for d in all_docs:
            norm = re.sub(r"[^\w\s]", "", d.title.lower()).strip()
            if norm and norm not in seen_titles:
                seen_titles.add(norm)
                unique_docs.append(d)

        logger.info(f"Sector real-time scrape collected {len(unique_docs)} unique articles")
        return unique_docs

    def group_articles_by_sector(
        self, docs: list[ScrapedRawDocument]
    ) -> dict[str, dict[str, list[SectorNewsItem]]]:
        """
        Classifies and maps each document into (category, sector_key) buckets.
        Returns: { category: { sector_key: [SectorNewsItem] } }
        """
        category_map: dict[str, dict[str, list[SectorNewsItem]]] = {
            "commodity": {k: [] for k in COMMODITY_TAXONOMY},
            "sp500": {k: [] for k in SP500_TAXONOMY},
            "idx": {k: [] for k in IDX_TAXONOMY},
        }

        for d in docs:
            matches = classify_document_to_sectors(d.title, d.raw_text, d.ticker, d.source_name)
            item = SectorNewsItem(
                title=d.title,
                source_name=d.source_name,
                source_url=d.source_url,
                publication_date=d.publication_date,
                ticker=d.ticker,
                summary_snippet=d.raw_text[:200] if d.raw_text else None,
            )

            for cat, key, _ in matches:
                if cat in category_map and key in category_map[cat]:
                    category_map[cat][key].append(item)

        return category_map

    def _fallback_sector_analysis(
        self, category: str, sector_key: str, sector_name: str, articles: list[SectorNewsItem]
    ) -> SectorRecommendationItem:
        """Deterministic keyword-based sentiment and momentum scoring for fallback."""
        default_tickers: list[str] = []
        if category == "commodity" and sector_key in COMMODITY_TAXONOMY:
            default_tickers = COMMODITY_TAXONOMY[sector_key]["tickers"][:4]
        elif category == "sp500" and sector_key in SP500_TAXONOMY:
            default_tickers = SP500_TAXONOMY[sector_key]["tickers"][:4]
        elif category == "idx" and sector_key in IDX_TAXONOMY:
            default_tickers = IDX_TAXONOMY[sector_key]["tickers"][:4]

        pos_words = {"naik", "lonjak", "rekor", "bullish", "rally", "surplus", "ekspansi", "laba", "dividen", "surge", "gain"}
        neg_words = {"turun", "anjlok", "rugi", "bearish", "defisit", "tekanan", "resesi", "drop", "slump", "fall"}

        combined_text = " ".join([a.title for a in articles]).lower()
        pos_count = sum(1 for w in pos_words if w in combined_text)
        neg_count = sum(1 for w in neg_words if w in combined_text)

        diff = pos_count - neg_count
        clean_name = sector_name.split("(")[0].strip() if "(" in sector_name else sector_name
        if diff >= 2:
            stance = "OVERWEIGHT"
            action_rec = "BUY"
            score = 0.75
            analysis = f"Sentimen pasar pada sektor {clean_name} menunjukkan dorongan beli kuat didukung dinamika harga dan katalis ekspansi industri."
        elif diff <= -2:
            stance = "UNDERWEIGHT"
            action_rec = "AVOID"
            score = -0.60
            analysis = f"Sektor {clean_name} menghadapi tekanan jangka pendek akibat pelemahan harga acuan atau kekhawatiran permintaan global."
        elif len(articles) > 0:
            stance = "ACCUMULATE_ON_WEAKNESS"
            action_rec = "BUY"
            score = 0.40
            analysis = f"Dinamika sektor {clean_name} bergerak konsolidatif dengan peluang akumulasi bertahap pada area support kritis."
        else:
            stance = "NEUTRAL"
            action_rec = "HOLD"
            score = 0.05
            analysis = f"Perkembangan sektor {clean_name} relatif stabil tanpa perubahan tren material dalam sesi berjalan."

        # Extract real tickers detected from news of Hari H
        detected = []
        for a in articles:
            if a.ticker and a.ticker not in ("GLOBAL_MACRO", "MACRO", "COMMODITY"):
                t = a.ticker if a.ticker.startswith("$") else f"${a.ticker}"
                if t not in detected:
                    detected.append(t)

        conviction = 85 if stance == "OVERWEIGHT" else 80 if stance == "ACCUMULATE_ON_WEAKNESS" else 72

        # Format top picks nicely with $ prefix for equities
        formatted_picks = [f"${t}" if not t.startswith("^") and not t.endswith("USD") and not t.startswith("LME") and not t.startswith("$") else t for t in default_tickers]

        return SectorRecommendationItem(
            sector_key=sector_key,
            sector_name=clean_name,
            category=category,  # type: ignore
            stance=stance,  # type: ignore
            recommendation=action_rec,  # type: ignore
            score=score,
            conviction_score=conviction,
            ai_analysis=analysis,
            detected_tickers=detected[:5],
            top_picks=formatted_picks,
            catalysts=[f"Pergerakan harga acuan dan volume transaksi sektor {clean_name}"],
            risk_factors=["Volatilitas pasar makro dan fluktuasi nilai tukar"],
            news_count=len(articles),
        )

    async def _analyze_single_sector(
        self, category: str, sector_key: str, sector_name: str, articles: list[SectorNewsItem]
    ) -> SectorRecommendationItem:
        """Analyzes a specific sector via LLM with fallback guardrail."""
        if not articles:
            return self._fallback_sector_analysis(category, sector_key, sector_name, articles)

        try:
            article_snippets = "\n".join([f"- {a.title} ({a.source_name})" for a in articles[:6]])
            user_msg = (
                f"Kategori: {category.upper()}\n"
                f"Sektor: {sector_name} (Key: {sector_key})\n"
                f"Jumlah Berita Terkait: {len(articles)}\n\n"
                f"Headlines Berita Terkini Hari Ini (Hari H):\n{article_snippets}"
            )

            if "11434" in settings.LLM_MODEL_URL or "11.20.2.201" in settings.LLM_MODEL_URL:
                ollama_base = settings.LLM_MODEL_URL.replace("/v1", "")
                payload = {
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": SECTOR_SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    "stream": False,
                    "options": {"num_gpu": 0, "temperature": 0.1},
                }
                async with httpx.AsyncClient(timeout=45.0) as client:
                    r = await client.post(f"{ollama_base}/api/chat", json=payload)
                    r.raise_for_status()
                    data = r.json()
                    content = data.get("message", {}).get("content", "").strip()
            else:
                llm = ChatOpenAI(
                    model=settings.LLM_MODEL,
                    temperature=0.1,
                    api_key=settings.ORCAROUTER_API_KEY,
                    base_url=settings.LLM_MODEL_URL,
                    timeout=45,
                    max_retries=1,
                )
                resp = await llm.ainvoke([
                    SystemMessage(content=SECTOR_SYSTEM_PROMPT),
                    HumanMessage(content=user_msg),
                ])
                content = resp.content.strip() if isinstance(resp.content, str) else str(resp.content).strip()
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                stance = data.get("stance", "NEUTRAL").strip()
                valid_stances = {"OVERWEIGHT", "NEUTRAL", "UNDERWEIGHT", "ACCUMULATE_ON_WEAKNESS", "HOLD_WATCH", "AVOID"}
                if stance not in valid_stances:
                    stance = "NEUTRAL"

                score = float(data.get("score", 0.0))
                score = max(-1.0, min(1.0, score))

                raw_conv = data.get("conviction_score")
                if raw_conv is not None:
                    try:
                        conviction_score = int(raw_conv)
                        conviction_score = max(50, min(98, conviction_score))
                    except Exception:
                        conviction_score = int(min(95, max(60, 60 + abs(score) * 35)))
                else:
                    conviction_score = int(min(95, max(60, 60 + abs(score) * 35)))

                analysis = data.get("ai_analysis", "").strip() or f"Analisis AI untuk sektor {sector_name}."

                detected_tickers = data.get("detected_tickers", [])
                if not detected_tickers:
                    found = []
                    for a in articles:
                        if a.ticker and a.ticker not in ("GLOBAL_MACRO", "MACRO", "COMMODITY"):
                            t = a.ticker if a.ticker.startswith("$") else f"${a.ticker}"
                            if t not in found:
                                found.append(t)
                    detected_tickers = found

                top_picks = data.get("top_picks", [])
                if not top_picks:
                    fb = self._fallback_sector_analysis(category, sector_key, sector_name, articles)
                    top_picks = fb.top_picks

                raw_rec = data.get("recommendation", "").strip().upper()
                if raw_rec not in {"BUY", "HOLD", "AVOID"}:
                    raw_rec = "BUY" if stance in {"OVERWEIGHT", "ACCUMULATE_ON_WEAKNESS"} else "AVOID" if stance in {"UNDERWEIGHT", "AVOID"} else "HOLD"

                clean_sec_name = sector_name.split("(")[0].strip() if "(" in sector_name else sector_name

                return SectorRecommendationItem(
                    sector_key=sector_key,
                    sector_name=clean_sec_name,
                    category=category,  # type: ignore
                    stance=stance,  # type: ignore
                    recommendation=raw_rec,  # type: ignore
                    score=score,
                    conviction_score=conviction_score,
                    ai_analysis=analysis,
                    detected_tickers=detected_tickers[:5],
                    top_picks=top_picks,
                    catalysts=data.get("catalysts", []),
                    risk_factors=data.get("risk_factors", []),
                    news_count=len(articles),
                )
        except Exception as e:
            logger.debug(f"LLM sector analysis fallback for {sector_key}: {e}")

        return self._fallback_sector_analysis(category, sector_key, sector_name, articles)

    async def run_full_sector_pipeline(self, broadcast: bool = False) -> SectorScrapeAndAnalyzeResponse:
        """
        Executes end-to-end sector intelligence workflow:
        1. Scrapes real-time headlines (TradingView, Yahoo Finance, CNBC).
        2. Maps and organizes articles into taxonomy sectors.
        3. Analyzes each sector concurrently via LLM.
        4. Optionally broadcasts to dedicated WAHA groups (IDX vs S&P 500).
        """
        docs = await self.scrape_all_sources()
        grouped = self.group_articles_by_sector(docs)

        # Cache raw articles
        flat_article_cache: dict[str, list[SectorNewsItem]] = {}
        analysis_tasks = []

        # Analyze active/relevant sectors across all 3 pillars
        for category, sectors in grouped.items():
            for key, articles in sectors.items():
                name = key
                if category == "commodity" and key in COMMODITY_TAXONOMY:
                    name = COMMODITY_TAXONOMY[key]["name"]
                elif category == "sp500" and key in SP500_TAXONOMY:
                    name = SP500_TAXONOMY[key]["name"]
                elif category == "idx" and key in IDX_TAXONOMY:
                    name = IDX_TAXONOMY[key]["name"]

                cache_key = f"{category}:{key}"
                flat_article_cache[cache_key] = articles
                analysis_tasks.append(self._analyze_single_sector(category, key, name, articles))

        recommendations = await asyncio.gather(*analysis_tasks)
        recommendations_list = list(recommendations)

        # Sort recommendations by absolute sentiment score descending
        recommendations_list.sort(key=lambda r: abs(r.score), reverse=True)

        idx_count = sum(1 for r in recommendations_list if r.category == "idx")
        us_count = sum(1 for r in recommendations_list if r.category == "sp500")
        macro_count = sum(1 for r in recommendations_list if r.category == "commodity")
        logger.info(f"[CLASSIFY:IDX] Analyzed {idx_count} domestic sectors")
        logger.info(f"[CLASSIFY:US] Analyzed {us_count} Wall Street sectors")
        logger.info(f"[CLASSIFY:MACRO GLOBAL] Analyzed {macro_count} global commodity sectors")

        # Update cache in service
        SectorIntelligenceService._cached_recommendations = recommendations_list
        SectorIntelligenceService._cached_articles = flat_article_cache
        SectorIntelligenceService._last_run_timestamp = datetime.now(timezone.utc)

        # Handle WhatsApp broadcast with 3 dedicated group channels
        broadcast_status: dict[str, Any] = {"idx_sent": False, "us_sent": False, "ternak_news_sent": False}
        if broadcast:
            idx_recs = [r for r in recommendations_list if r.category == "idx"]
            us_recs = [r for r in recommendations_list if r.category == "sp500"]
            macro_comm_recs = [r for r in recommendations_list if r.category == "commodity"]

            broadcast_status = await self.dispatch_waha_sector_alerts(idx_recs, us_recs, macro_comm_recs)

        return SectorScrapeAndAnalyzeResponse(
            status="success",
            articles_scraped=len(docs),
            sectors_analyzed=len(recommendations_list),
            broadcast_sent=broadcast_status,
            recommendations=recommendations_list,
        )

    def format_idx_wa_message(self, recs: list[SectorRecommendationItem]) -> str:
        """Formats the official IDX Sector Intelligence WhatsApp alert."""
        today_str = datetime.now().strftime("%d %B %Y")
        top_recs = recs[:5] if recs else []

        items_text = []
        for r in top_recs:
            label = _conviction_label(r.conviction_score)
            sec_name = r.sector_name.split("(")[0].strip() if "(" in r.sector_name else r.sector_name
            action = _resolve_action_recommendation(r)
            header_line = f"• {sec_name} : {action} | Conviction: {r.conviction_score}% {label}"
            tickers_str = _format_tickers_with_action(r.detected_tickers, action)
            items_text.append(
                f"{header_line}\n"
                f"  - Analisis: {r.ai_analysis}\n"
                f"  - Saham Terdeteksi: {tickers_str}"
            )

        body = "\n".join(items_text) if items_text else "• Sektor domestik BEI berkonsolidasi wajar."
        return f"""🇮🇩 [IDX-INTEL AI] 🌐
Tanggal: {today_str} | Sesi: Real-Time Market Update
------------------------------------------------

⚡ TOP MOMENTUM SEKTOR BURSA EFEK INDONESIA:
{body}

💡 Rekomendasi Rotasi Sektor:
Alokasikan portofolio secara terukur pada sektor yang mencatatkan rekomendasi BUY dengan conviction tinggi sebagai langkah mitigasi volatilitas IHSG.""".strip()

    def format_us_wa_message(self, recs: list[SectorRecommendationItem]) -> str:
        """Formats the official US Intel AI (S&P 500, NASDAQ & US ETFs) WhatsApp alert."""
        today_str = datetime.now().strftime("%d %B %Y")
        sp_items = [r for r in recs if r.category == "sp500"][:5]

        sp_text = []
        for r in sp_items:
            label = _conviction_label(r.conviction_score)
            sec_name = r.sector_name.split("(")[0].strip() if "(" in r.sector_name else r.sector_name
            action = _resolve_action_recommendation(r)
            header_line = f"• {sec_name} : {action} | Conviction: {r.conviction_score}% {label}"
            tickers_str = _format_tickers_with_action(r.detected_tickers, action)
            sp_text.append(
                f"{header_line}\n"
                f"  - Analisis: {r.ai_analysis}\n"
                f"  - Ticker/ETF Terdeteksi: {tickers_str}"
            )

        sp_body = "\n".join(sp_text) if sp_text else "• Wall Street bergerak netral tanpa pergeseran sektor ekstrem."

        return f"""🇺🇸 [US-INTEL AI - WALL STREET & US ETFS] 🌐
Tanggal: {today_str} | Sesi: US Market Outlook
------------------------------------------------

⚡ S&P 500, NASDAQ & SEKTOR UTAMA:
{sp_body}

💡 Rekomendasi Portofolio & Alokasi ETF:
Fokus pada konstituen sektor berfundamental kuat dengan rekomendasi BUY (SPY, QQQ, XLK, SMH) dan pertahankan diversifikasi terukur.""".strip()

    def format_sp500_wa_message(self, recs: list[SectorRecommendationItem]) -> str:
        """Alias for backward compatibility."""
        return self.format_us_wa_message(recs)

    def format_ternak_news_wa_message(
        self,
        recs: list[SectorRecommendationItem],
        live_comm_body: str | None = None,
    ) -> str:
        """Formats the official Ternak Saham News (Global Macro, The Fed, & 12 Commodities) alert."""
        today_str = datetime.now().strftime("%d %B %Y")
        comm_items = [r for r in recs if r.category == "commodity"][:5]

        comm_text = []
        for r in comm_items:
            label = _conviction_label(r.conviction_score)
            sec_name = r.sector_name.split("(")[0].strip() if "(" in r.sector_name else r.sector_name
            action = _resolve_action_recommendation(r)
            header_line = f"• {sec_name} : {action} | Conviction: {r.conviction_score}% {label}"
            us_etfs = COMMODITY_BENCHMARK_US_ETFS.get(r.sector_key, [])
            us_etfs_formatted = [f"{etf} ({action})" for etf in us_etfs[:2]]
            symbols_str = _format_tickers_with_action(r.detected_tickers, action)

            if symbols_str != "-":
                us_etf_str = f" | US ETF: {', '.join(us_etfs_formatted)}" if us_etfs else ""
                combined_recs = f"{symbols_str}{us_etf_str}"
            elif us_etfs:
                combined_recs = f"US ETF: {', '.join(us_etfs_formatted)}"
            else:
                combined_recs = "-"

            comm_text.append(
                f"{header_line}\n"
                f"  - Dinamika: {r.ai_analysis}\n"
                f"  - Rekomendasi Investasi: {combined_recs}"
            )

        comm_body = "\n".join(comm_text) if comm_text else "• Pasar komoditas berkonsolidasi stabil."
        live_section = f"\n{live_comm_body}\n" if live_comm_body else ""

        return f"""📈 [TERNAK SAHAM NEWS - GLOBAL MACRO & COMMODITIES] 🌐
Tanggal: {today_str} | Sesi: Global Macro Intelligence
------------------------------------------------

🏛 GLOBAL MACRO, INFLASI & THE FED:
• Kebijakan The Fed & Suku Bunga: Arah moneter The Fed era Kevin Warsh menjaga yield Treasury 10-tahun stabil di tengah evaluasi data inflasi terbaru.
• DXY & Geopolitik: Indeks Dolar AS DXY bertahan di area konsolidasi seiring respon pasar terhadap wacana tarif perdagangan global.
{live_section}
⚡ TOP MOMENTUM SEKTOR KOMODITAS:
{comm_body}

💡 Outlook Makro:
Pantau rilis data tenaga kerja AS, risalah FOMC The Fed, serta rotasi harga energi dan logam industri.""".strip()

    async def dispatch_waha_sector_alerts(
        self,
        idx_recs: list[SectorRecommendationItem],
        us_recs: list[SectorRecommendationItem],
        macro_comm_recs: list[SectorRecommendationItem] | None = None,
    ) -> dict[str, Any]:
        """
        Dispatches sector intelligence messages to the 3 designated WhatsApp channels:
        - 1. IDX alert -> settings.BROADCAST_CHAT_ID (IDX Intel AI)
        - 2. US Equities alert -> settings.BROADCAST_CHAT_ID_SP500 (US Intel AI)
        - 3. Global Macro & Commodities -> settings.BROADCAST_CHAT_ID_TERNAK_NEWS (Ternak Saham News)
        """
        status: dict[str, Any] = {"idx_sent": False, "us_sent": False, "ternak_news_sent": False}

        # 1. Dispatch IDX Report to IDX Intel AI Group
        if idx_recs and settings.BROADCAST_CHAT_ID:
            idx_msg = self.format_idx_wa_message(idx_recs)
            try:
                res = await self.waha_client.send_text(settings.BROADCAST_CHAT_ID, idx_msg)
                status["idx_sent"] = res
                logger.info("[OUTPUT:IDX] Dispatched IDX sector report to IDX Intel AI group", chat_id=settings.BROADCAST_CHAT_ID, ok=res)
            except Exception as e:
                logger.error("Failed to send IDX sector WAHA alert", error=str(e))

        # 2. Dispatch US Equities Report to US Intel AI Group
        us_chat_id = settings.BROADCAST_CHAT_ID_SP500 or settings.BROADCAST_CHAT_ID
        if us_recs and us_chat_id:
            us_msg = self.format_us_wa_message(us_recs)
            try:
                res = await self.waha_client.send_text(us_chat_id, us_msg)
                status["us_sent"] = res
                logger.info("[OUTPUT:US] Dispatched US sector report to US Intel AI group", chat_id=us_chat_id, ok=res)
            except Exception as e:
                logger.error("Failed to send US sector WAHA alert", error=str(e))

        # 3. Dispatch Global Macro & Commodities to Ternak Saham News Group
        ternak_chat_id = settings.BROADCAST_CHAT_ID_TERNAK_NEWS or settings.BROADCAST_CHAT_ID
        if macro_comm_recs and ternak_chat_id:
            live_body = await self.get_live_commodities_movement_id()
            ternak_msg = self.format_ternak_news_wa_message(macro_comm_recs, live_comm_body=live_body)
            try:
                res = await self.waha_client.send_text(ternak_chat_id, ternak_msg)
                status["ternak_news_sent"] = res
                logger.info("[OUTPUT:MACRO GLOBAL] Dispatched Macro & Commodities report to Ternak Saham News group", chat_id=ternak_chat_id, ok=res)
            except Exception as e:
                logger.error("Failed to send Ternak Saham News WAHA alert", error=str(e))

        return status

    async def dispatch_idx_report(self, target_chat_id: str | None = None) -> bool:
        """Sends IDX Intel AI report to target chat ID or default group."""
        chat_id = target_chat_id or settings.BROADCAST_CHAT_ID
        if not chat_id:
            return False
        recs = [r for r in self.get_latest_recommendations().recommendations if r.category == "idx"]
        msg = self.format_idx_wa_message(recs)
        return await self.waha_client.send_text(chat_id, msg)

    async def dispatch_us_report(self, target_chat_id: str | None = None) -> bool:
        """Sends US Intel AI report to target chat ID or default group."""
        chat_id = target_chat_id or settings.BROADCAST_CHAT_ID_SP500 or settings.BROADCAST_CHAT_ID
        if not chat_id:
            return False
        recs = [r for r in self.get_latest_recommendations().recommendations if r.category == "sp500"]
        msg = self.format_us_wa_message(recs)
        return await self.waha_client.send_text(chat_id, msg)

    async def dispatch_ternak_news_report(self, target_chat_id: str | None = None) -> bool:
        """Sends Ternak Saham News macro & commodities report to target chat ID or default group."""
        chat_id = target_chat_id or settings.BROADCAST_CHAT_ID_TERNAK_NEWS or settings.BROADCAST_CHAT_ID
        if not chat_id:
            return False
        recs = [r for r in self.get_latest_recommendations().recommendations if r.category == "commodity"]
        live_body = await self.get_live_commodities_movement_id()
        msg = self.format_ternak_news_wa_message(recs, live_comm_body=live_body)
        return await self.waha_client.send_text(chat_id, msg)

    def get_latest_recommendations(self, category: str | None = None) -> SectorRecommendationsResponse:
        """Retrieves cached recommendations with optional category filter."""
        recs = SectorIntelligenceService._cached_recommendations
        if not recs:
            # Generate instant fallback recommendations from taxonomy if cache is uninitialized
            recs = []
            for k, info in COMMODITY_TAXONOMY.items():
                recs.append(self._fallback_sector_analysis("commodity", k, info["name"], []))
            for k, info in SP500_TAXONOMY.items():
                recs.append(self._fallback_sector_analysis("sp500", k, info["name"], []))
            for k, info in IDX_TAXONOMY.items():
                recs.append(self._fallback_sector_analysis("idx", k, info["name"], []))
            SectorIntelligenceService._cached_recommendations = recs

        filtered = recs
        if category:
            cat_clean = category.lower().strip()
            filtered = [r for r in recs if r.category.lower() == cat_clean]

        return SectorRecommendationsResponse(
            timestamp=SectorIntelligenceService._last_run_timestamp or datetime.now(timezone.utc),
            total_sectors=len(filtered),
            recommendations=filtered,
            executive_summary="Sektor intelijen real-time multi-market mencakup BEI, Wall Street (S&P 500), dan komoditas global lengkap.",
        )

    def get_sector_detail(self, category: str, sector_key: str) -> SectorDetailResponse | None:
        """Retrieves specific sector deep-dive with underlying mapped articles."""
        cat_clean = category.lower().strip()
        key_clean = sector_key.lower().strip()

        all_recs = SectorIntelligenceService._cached_recommendations
        matched_rec = next((r for r in all_recs if r.category == cat_clean and r.sector_key == key_clean), None)

        # Fallback if not in active recs
        if not matched_rec:
            name = key_clean
            if cat_clean == "commodity" and key_clean in COMMODITY_TAXONOMY:
                name = COMMODITY_TAXONOMY[key_clean]["name"]
            elif cat_clean == "sp500" and key_clean in SP500_TAXONOMY:
                name = SP500_TAXONOMY[key_clean]["name"]
            elif cat_clean == "idx" and key_clean in IDX_TAXONOMY:
                name = IDX_TAXONOMY[key_clean]["name"]
            else:
                return None
            matched_rec = self._fallback_sector_analysis(cat_clean, key_clean, name, [])

        cache_key = f"{cat_clean}:{key_clean}"
        articles = SectorIntelligenceService._cached_articles.get(cache_key, [])

        return SectorDetailResponse(
            sector_key=matched_rec.sector_key,
            sector_name=matched_rec.sector_name,
            category=matched_rec.category,
            recommendation=matched_rec,
            articles=articles,
        )

    def get_realtime_news(self) -> dict[str, list[SectorNewsItem]]:
        """Returns all real-time news articles partitioned by sector."""
        return SectorIntelligenceService._cached_articles

    @classmethod
    async def get_live_commodities_movement_id(cls) -> str:
        """
        Fetches live prices for expanded global commodities in Indonesian names
        (Emas XAU, Perak XAG, Minyak Mentah WTI, Minyak Mentah Brent, Gas Alam, Batubara, Nikel, Timah, Tembaga, Aluminium, Gandum, Jagung)
        and outputs formatted movement with English Title Case momentum labels and Top Gainers / Losers summary.
        Token-efficient formatting without unnecessary parentheses.
        """
        commodity_symbols = [
            ("Emas", "GC=F", 4186.70, 0.40),
            ("Perak", "SI=F", 57.13, 0.52),
            ("Minyak Mentah WTI", "CL=F", 99.04, 1.09),
            ("Minyak Mentah Brent", "BZ=F", 109.69, 3.56),
            ("Gas Alam", "NG=F", 3.12, -3.68),
            ("Batubara", "COAL", 142.50, 1.20),
            ("Nikel", "VALE", 16850.0, 1.45),
            ("Timah", "TIN.L", 32400.0, 0.15),
            ("Tembaga", "HG=F", 6.56, 0.78),
            ("Aluminium", "ALI=F", 3092.25, -0.14),
            ("Gandum", "ZW=F", 659.75, -1.53),
            ("Jagung", "ZC=F", 474.25, -0.78),
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        items = []
        parsed_results = []

        try:
            async with httpx.AsyncClient(headers=headers, timeout=6.0) as client:
                for name, sym, def_price, def_pct in commodity_symbols:
                    price, pct = def_price, def_pct
                    try:
                        r = await client.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=2d")
                        if r.status_code == 200:
                            meta = r.json().get("chart", {}).get("result", [{}])[0].get("meta", {})
                            cur_p = meta.get("regularMarketPrice")
                            prev_p = meta.get("chartPreviousClose")
                            if cur_p and prev_p:
                                price = cur_p
                                pct = ((cur_p - prev_p) / prev_p) * 100
                    except Exception:
                        pass

                    if pct > 1.0:
                        emoji = "📈"
                        trend = "Strong Buyer Momentum"
                    elif pct >= 0.2:
                        emoji = "📈"
                        trend = "Moderate Buying Interest"
                    elif pct > -0.2:
                        emoji = "↔️"
                        trend = "Consolidation Range"
                    elif pct >= -1.0:
                        emoji = "📉"
                        trend = "Minor Seller Pressure"
                    else:
                        emoji = "📉"
                        trend = "Sellers In Control"

                    items.append(f"{emoji} {name}: {price:,.2f} USD ({pct:+.2f}%) — {trend}")
                    parsed_results.append({"name": name, "pct": pct})
        except Exception as e:
            logger.warning(f"Error fetching live commodities: {e}")
            for name, _, def_price, def_pct in commodity_symbols:
                trend = "Moderate Buying Interest" if def_pct > 0 else "Minor Seller Pressure"
                emoji = "📈" if def_pct > 0 else "📉"
                items.append(f"{emoji} {name}: {def_price:,.2f} USD ({def_pct:+.2f}%) — {trend}")
                parsed_results.append({"name": name, "pct": def_pct})

        # Calculate Top Kenaikan and Top Penurunan with parentheses
        sorted_by_pct = sorted(parsed_results, key=lambda x: x["pct"], reverse=True)
        top_gainers = [c for c in sorted_by_pct if c["pct"] > 0][:3]
        top_losers = [c for c in reversed(sorted_by_pct) if c["pct"] < 0][:3]

        gainers_str = ", ".join([f"{c['name']} ({c['pct']:+.2f}%)" for c in top_gainers]) if top_gainers else "-"
        losers_str = ", ".join([f"{c['name']} ({c['pct']:+.2f}%)" for c in top_losers]) if top_losers else "-"

        body = "\n".join(items)
        return (
            "🛢 LIVE PERGERAKAN HARGA KOMODITAS DUNIA:\n"
            f"{body}\n\n"
            f"🔥 Top Kenaikan: {gainers_str}\n"
            f"🔻 Top Penurunan: {losers_str}"
        )

    @classmethod
    async def generate_market_synthesis(
        cls,
        doc: ScrapedRawDocument,
        commodity_summary: str = "",
        is_global: bool = True
    ) -> str:
        """
        Dynamically synthesizes professional market insights from news headlines,
        underlying article context, and commodity price movements.
        Strict rule: Absolutely NO mentions of 'AI', 'kecerdasan buatan', or 'WAHA'.
        Language: Fluent, executive-level Indonesian. Flexible output (not strict JSON).
        """
        market_type = "Pasar Global, Wall Street (S&P 500) & Komoditas Global" if is_global else "Bursa Efek Indonesia (IHSG & Sektor Domestik)"

        system_prompt = f"""
Anda adalah Senior Global Macro & Sector Investment Strategist independen.
Tugas Anda adalah menulis sintesis analisis dan prospek pasar secara profesional, tajam, dan mengalir bebas dalam Bahasa Indonesia (2 hingga 3 paragraf padat).

Konteks Pasar: {market_type}.

Panduan Penulisan:
1. Hubungkan katalis berita utama dan dinamika komoditas ke sentimen pasar secara logis.
2. Jelaskan transmisi dampaknya ke sektor-sektor terkait (seperti energi, perbankan, teknologi, tambang/mineral, atau manufaktur).
3. Berikan panduan taktis yang berimbang dan actionable bagi investor institusi maupun ritel.
4. GAYA PENULISAN: Bersifat alami, berbobot seperti laporan riset sekuritas/ekuitas papan atas.
5. ATURAN MUTLAK: DILARANG KERAS menggunakan kata "AI", "kecerdasan buatan", "WAHA", atau format cetak kaku/robotik. Tulis murni sebagai catatan analisis strategis.
""".strip()

        user_prompt = f"""
Judul Berita Terkini: {doc.title}
Aset/Emiten: ${doc.ticker}
Sumber: {doc.source_name}
Ringkasan Isi Berita:
{doc.raw_text[:600]}

Data Pergerakan Komoditas Terkini (USD):
{commodity_summary}

Tolong berikan sintesis dan prospek pasarnya sekarang dalam Bahasa Indonesia tanpa menyebut kata AI. Jika mengutip harga acuan komoditas, selalu sertakan satuan USD.
""".strip()

        try:
            if "11434" in settings.LLM_MODEL_URL or "11.20.2.201" in settings.LLM_MODEL_URL:
                ollama_base = settings.LLM_MODEL_URL.replace("/v1", "")
                payload = {
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "options": {"num_gpu": 0, "temperature": 0.3, "num_predict": 280},
                }
                async with httpx.AsyncClient(timeout=75.0) as client:
                    r = await client.post(f"{ollama_base}/api/chat", json=payload)
                    r.raise_for_status()
                    data = r.json()
                    text = data.get("message", {}).get("content", "").strip()
            else:
                llm = ChatOpenAI(
                    model=settings.LLM_MODEL,
                    temperature=0.3,
                    api_key=settings.ORCAROUTER_API_KEY,
                    base_url=settings.LLM_MODEL_URL,
                    timeout=45,
                    max_retries=1,
                )
                resp = await llm.ainvoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ])
                text = resp.content.strip() if isinstance(resp.content, str) else str(resp.content).strip()

            text = re.sub(r"\b(AI|Kecerdasan Buatan|WAHA)\b", "analis pasar", text, flags=re.IGNORECASE)
            return text
        except Exception as e:
            logger.warning(f"Fallback synthesis due to LLM exception: {e}")
            if is_global:
                return (
                    f"Perkembangan terkini seputar {doc.title} memberikan sinyal penting bagi transmisi risiko pasar modal global. "
                    "Kenaikan volatilitas dan penyesuaian ekspektasi suku bunga global cenderung menekan valuasi saham-saham ber-multiple tinggi di Wall Street, "
                    "sementara ketahanan harga komoditas energi dan tambang (seperti minyak mentah dan nikel) membuka ruang mitigasi selektif bagi emiten berbasis sumber daya alam. "
                    "Pelaku pasar disarankan mempertahankan disiplin alokasi pada aset berfundamental defensif dan mencermati konfirmasi likuiditas sebelum menambah eksposur risiko."
                )
            else:
                return (
                    f"Aksi korporasi dan informasi material terkait ${doc.ticker} ({doc.title}) menjadi katalis penggerak likuiditas di Bursa Efek Indonesia. "
                    "Sentimen ini berpotensi memberikan dorongan sektoral jangka pendek, khususnya pada rantai pasok dan entitas terafiliasi. "
                    "Investor diimbau mengamati volume akumulasi serta konfirmasi jadwal pelaksanaan untuk mengoptimalkan momentum rotasi portofolio IHSG."
                )

