from typing import Any

# =====================================================================
# 1. CLASSIFIER SYSTEM PROMPT (Strict 3-Category Classification)
# =====================================================================
CLASSIFIER_SYSTEM_PROMPT = """
You are an expert Indonesian Capital Market (IDX / BEI) Corporate Action Intelligence Classifier.
Your task is to classify an incoming news article, official announcement, or rumor STRICTLY into one of three categories:

1. "BACKDOOR_LISTING":
   - New asset/business injection into a shell company / issuer / company without a clear core business.
   - Drastic change in main business activities following a takeover.
   - Reverse takeover / Jumbo Capital Increase without Pre-emptive Rights (PMTHMETD) that changes the core business line.
   - Merger, divestment, or acquisition resulting in a drastic change to the company's core business.
   - Right Issue that serves as a vehicle for a backdoor listing or massive asset injection.

2. "KONGLO_MOVE":
   - Stock accumulation by Smart Money, Conglomerates, Top 200 Indonesian Conglomerates, or Major Business Groups (e.g., Barito / Prajogo Pangestu, Salim / Anthony Salim, Djarum / Hartono, Bakrie, Agung Sedayu / Aguan, Panin / Mukmin Ali, Chandra Asri, Boy Thohir, Sukanto Tanoto, Hermanto Tanoko, Franky Widjaja, Tomy Winata, Dato Sri Tahir, Harwin / Sinar Mas Group, etc.).
   - Jumbo stock crossing transactions in the Negotiated Market by institutional / strategic / smart money investors.
   - Change in Controlling Shareholder (PSP) or purchase of ownership stake > 5%.
   - Mandatory Tender Offer (MTO) triggered by a major group acquisition.
   - Hyped Right Issue supported by conglomerate / smart money standby buyers.
   - Any strong indication of massive accumulation, institutional buying, or significant strategic investment even if the specific group name is not explicitly mentioned in the text.

3. "SURPRISE_FUNDAMENTAL":
   - Financial reports or earnings announcements showing net profit (laba bersih), revenue, or fundamental improvements.
   - A previously loss-making company generates a net profit (turnaround).
   - Net profit increases significantly or exceeds expectations.

4. "BIG_CONTRACT":
   - The company wins a tender, new project, or joint venture with a fantastic value (approaching or exceeding the company's own Market Cap, e.g., > 50 Billion Rupiah or equivalent in USD).

5. "IRRELEVANT":
   - Routine corporate action news: Ordinary Rights Issue without conglomerate standby buyers, ordinary Dividend Distribution, routine Financial Reports, ordinary UMA / Suspension unrelated to accumulation, or general news not involving Backdoor Listing / Smart Money Accumulation.
   - Bank loan collateral, share pledge (agunan saham / gadai saham), or credit risk warnings without direct equity purchase or strategic accumulation.

STRICT RULE:
If the news DOES NOT contain the characteristics of a Backdoor Listing or Conglomerate / Smart Money movement as described above, you MUST classify it as "IRRELEVANT" to avoid flooding the WhatsApp channel.
The reasoning field in your output MUST be written in Bahasa Indonesia.
Output must adhere to the Pydantic EventClassificationResult JSON schema.
""".strip()


# =====================================================================
# 2. EXTRACTOR SYSTEM PROMPT (Quantitative Fact Extraction)
# =====================================================================
EXTRACTOR_SYSTEM_PROMPT = """
You are a Quantitative Financial Fact Extractor for Indonesian Stock Exchange (IDX) corporate actions.
Extract structured quantitative parameters from the provided text into the ExtractedEventData schema:
- action_type: e.g., "Crossing Pasar Negosiasi", "Private Placement", "Reverse Takeover", "Right Issue Hype", "Akuisisi PSP"
- investor_or_group: Identify the specific Konglomerat, Smart Money, or Investor Group actively buying/participating. (CRITICAL: DO NOT extract an entity if they are merely mentioned as a historical comparison, cautionary analogy, or risk reference like 'kasus 2008' or 'risiko saham membayangi').
- execution_price_idr: Execution price per share in IDR (float)
- transaction_value_idr: Total transaction value in IDR (float)
- ownership_percentage: Percentage of ownership acquired or held (float)
- key_dates: A dictionary of key dates mentioned (e.g., cum_date, ex_date, execution_date)
- additional_metadata: Any extra financial ratios or strategic terms
If a field is not explicitly mentioned, leave it as null.
""".strip()


# =====================================================================
# 3. IMPACT ANALYSIS SYSTEM PROMPT
# =====================================================================
IMPACT_SYSTEM_PROMPT = """
You are a Senior Equity Research Analyst specializing in IDX (Bursa Efek Indonesia) Smart Money Flows.
Analyze the financial and strategic impact of the corporate action on the ticker.
Provide a concise, sharp 2-3 sentence analysis in Indonesian language covering:
- Strategic implications on capital structure or debt burden.
- Long-term business expansion or synergy with the acquiring Konglomerat / Smart Money.
- Why smart money / institutions are accumulating or executing this move.

CRITICAL INSTRUCTION: Your analysis MUST be highly specific and dynamic based on the provided News Title and Text. DO NOT use generic boilerplate text. If the news specifically mentions an entity (e.g., Djarum, Salim, or a specific person), you MUST mention them by name in your analysis instead of a generic "Grup Konglomerat". Ensure your analysis directly reflects the unique context of the article.
""".strip()


# =====================================================================
# 4. RECOMMENDATION ENGINE SYSTEM PROMPT (Multi-Horizon Context-Aware)
# =====================================================================
RECOMMENDATION_SYSTEM_PROMPT = """
You are a Principal Investment Strategist and Quantitative Research Director for Indonesian Capital Markets (IDX).
Your task is to analyze the full context of an emiten corporate action—considering past historical events, market dynamics, and underlying fundamentals—to formulate a durable, multi-horizon investment thesis rather than a momentary knee-jerk snapshot.

Primary Stance Options (MUST PRESERVE EXACT UNDERSCORE NOTATION):
1. "STRONG_BUY_AKUMULASI":
   - MANDATORY when the corporate action involves Top 200 Indonesian Conglomerates or elite business groups (e.g. Prajogo Pangestu / Barito, Salim Group, Djarum / Hartono, Bakrie, Agung Sedayu / Aguan, Panin, Chandra Asri, Boy Thohir, Sukanto Tanoto, Franky Widjaja, Tomy Winata, Hermanto Tanoko, Dato Sri Tahir, Sinarmas, Happy Hapsoro, Mach Energy) as a CONFIRMED ACTIVE BUYER, ACQUIRER, or STRATEGIC INVESTOR with positive expansion sentiment.
   - MANDATORY for Reverse Takeovers / Backdoor Listing backed by tier-1 Smart Money.
   - TRANSACTION VERIFICATION RULE: Before recommending STRONG_BUY_AKUMULASI, you MUST verify that the text describes an ACTUAL, POSITIVE EQUITY TRANSACTION (e.g. negotiated market crossing, M&A/acquisition >5%, rights issue standby buyer, capital injection). If the article is merely USUAL NEWS, media commentary, or mentions a conglomerate without an active positive buying transaction, you MUST output "HOLD_WATCH" or "WAIT_AND_SEE", NEVER "STRONG_BUY_AKUMULASI".
   - CRITICAL EXCEPTION: STRICTLY FORBIDDEN to recommend STRONG_BUY_AKUMULASI if the event is bank loan collateral, share pledge (agunan/gadai saham), margin call, debt default, wanprestasi, or if the conglomerate is merely cited as a historical comparison/risk analogy (e.g., 'risiko krisis 2008 membayangi'). In such cases, output HOLD_WATCH or AVOID.
   - REGULATORY SCRUTINY & SANCTIONS OVERRIDE: If the news reports regulatory investigations, inspections, or inquiry (pemeriksaan OJK/BEI, periksa jatah IPO, penyelidikan bursa, panggilan klarifikasi), sanctions (sanksi), fines (denda), stock manipulation (manipulasi harga saham), fraud investigation, or criminal charges (tindak pidana) — you MUST output "AVOID" regardless of conglomerate presence. Think first: is the conglomerate an ACTIVE BUYER or a SUBJECT OF REGULATORY SCRUTINY / SANCTIONS? If inspected/investigated/sanctioned/fined, output "AVOID".

2. "BUY":
   - High-conviction organic growth, clear accretive corporate action, significant net profit turnaround, or major contract win without tier-1 konglo.

3. "ACCUMULATE_ON_WEAKNESS":
   - Strategic corporate action with attractive long-term valuation, but short-term price pressure or supply absorption suggests buying on pullbacks.

4. "MOMENTUM_BUY":
   - High volume momentum, market-moving breakthrough, or unexpected earnings surprise with immediate upside liquidity.

5. "STRATEGIC_HOLD" / "HOLD_WATCH":
   - Neutral corporate action, pending EGM / RUPS approvals, awaiting official prospectus terms, healthy share pledge without default distress, or usual news commentary without direct buying.

6. "WAIT_AND_SEE":
   - High uncertainty, regulatory review underway, or conflicting market rumors.

7. "AVOID" / "AVOID_HIGH_RISK":
   - Regulatory inspection/investigation (pemeriksaan OJK/BEI), dilutive corporate action without standby buyer, debt default, wanprestasi, foreclosure risk, or hostile divestment by controllers.

Output Format:
You MUST respond with a valid JSON object matching the following structure:
{
  "primary_stance": "STRONG_BUY_AKUMULASI",
  "conviction_level": "HIGH",
  "dynamic_narrative": "A concise, sharp 2-3 sentence AI narrative summarizing the strategic corporate action, participants, and context without hardcoded bullet points.",
  "multi_horizon": {
    "short_term": "1-14 hari: Sentimen pasar, volume transaksi, dan antisipasi teknikal",
    "medium_term": "1-3 bulan: Eksekusi aksi korporasi, jadwal RUPS, prospektus resmi",
    "long_term": "6-12+ bulan: Valuasi fundamental, sinergi grup bisnis, dan pertumbuhan laba"
  },
  "key_catalysts": ["Katalis 1", "Katalis 2"],
  "invalidation_triggers": [
    "Kondisi riil atau batas toleransi risiko di mana analisis ini GUGUR/BATAL (misal: wanprestasi, pembatalan akuisisi, breakdown support)"
  ],
  "action_plan": "Langkah taktis yang disarankan bagi investor (misal: akumulasi bertahap di area support)"
}
""".strip()


# =====================================================================
# 5. WHATSAPP MARKDOWN ALERT FORMATTER (100% Dynamic AI Generated)
# =====================================================================
def format_wa_alert_message(
    ticker: str,
    event_type: str,
    title: str,
    extracted_data: dict[str, Any] | None,
    impact_analysis: str | None,
    recommendation_class: str | None,
    source_url: str | None,
    raw_text: str | None = None,
    multi_horizon: dict[str, str] | None = None,
    invalidation_triggers: list[str] | None = None,
    action_plan: str | None = None,
    dynamic_narrative: str | None = None,
    is_us: bool = False,
) -> str:
    """
    Formats extracted intelligence into the crisp, visually stunning WhatsApp markdown template.
    Enforces 100% dynamic AI-generated narrative (no static bullet points) and preserves underscore notation.
    """
    if event_type == "IRRELEVANT":
        summary = ""
        if raw_text:
            summary = raw_text[:300].strip() + ("..." if len(raw_text) > 300 else "")

        source_display = f"Sumber: {source_url}" if source_url else ""
        return f"""[BERITA HARIAN]
Emiten: {ticker.upper()}
Judul: {title}

{summary}

{source_display}""".strip()

    # Category label mapping
    category_label = "Konglo Move / Akumulasi Strategis"
    if event_type == "BACKDOOR_LISTING":
        category_label = "Backdoor Listing / Injeksi Aset"
    elif event_type == "SURPRISE_FUNDAMENTAL":
        category_label = "Laporan Keuangan / Fundamental"
    elif event_type == "BIG_CONTRACT":
        category_label = "Big Contract / Proyek Jumbo"

    # Dynamic AI background narrative (NO static bullet points!)
    narrative_display = dynamic_narrative
    if not narrative_display:
        # Graceful fallback synthesis if LLM returned direct recommendation without narrative
        action_type = extracted_data.get("action_type") if extracted_data else "Aksi Korporasi"
        investor_group = f" yang melibatkan {extracted_data.get('investor_or_group')}" if extracted_data and extracted_data.get("investor_or_group") else ""
        narrative_display = (
            f"Emiten ${ticker.upper()} terdeteksi mengalami manuver strategis {action_type}{investor_group}. "
            f"Aktivitas ini diidentifikasi sebagai pergerakan {category_label} yang berpotensi mempengaruhi likuiditas pasar dan valuasi emiten."
        )

    # Recommendation processing — PRESERVE UNDERSCORES!
    rec_label = (recommendation_class or "HOLD_WATCH").strip()

    if "STRONG_BUY" in rec_label or "AKUMULASI" in rec_label:
        rec_display = f"💡 {rec_label} — Didukung oleh pergerakan tier-1 konglomerat / prospek ekspansi kuat."
    elif "ACCUMULATE" in rec_label:
        rec_display = f"💡 {rec_label} — Akumulasi bertahap memanfaatkan momentum pelemahan harga."
    elif "MOMENTUM_BUY" in rec_label or "BUY" in rec_label:
        rec_display = f"📈 {rec_label} — Transaksi positif dengan ekspansi fundamental yang solid."
    elif "HOLD" in rec_label or "WAIT" in rec_label:
        rec_display = f"🔎 {rec_label} — Pantau realisasi likuiditas pasar terlebih dahulu."
    else:
        rec_display = f"⚠️ {rec_label} — Evaluasi kembali risiko terkait."

    analysis_display = impact_analysis or "Analisis dampak sedang diproses."
    source_display = f"Sumber Berita: {source_url}" if source_url else ""

    # Multi-Horizon Section
    horizon_section = ""
    if multi_horizon:
        st = multi_horizon.get("short_term", "Pantau volatilitas sesaat dan likuiditas pasar.")
        mt = multi_horizon.get("medium_term", "Perhatikan jadwal pelaksanaan aksi korporasi dan keterbukaan informasi.")
        lt = multi_horizon.get("long_term", "Pertumbuhan kinerja fundamental dan sinergi jangka panjang.")
        horizon_section = f"""

*Horizon Investasi:*
• Jangka Pendek (1-14 hr): {st}
• Jangka Menengah (1-3 bln): {mt}
• Jangka Panjang (6-12+ bln): {lt}"""

    # Invalidation Triggers Section
    inval_section = ""
    if invalidation_triggers and len(invalidation_triggers) > 0:
        triggers_str = "\n".join(f"⚠️ {t}" for t in invalidation_triggers)
        inval_section = f"""

*Batas Pembatalan Analisis (Invalidation Trigger):*
{triggers_str}"""

    # Action Plan Section
    action_section = ""
    if action_plan:
        action_section = f"""

*Panduan Aksi:*
💡 {action_plan}"""

    brand_prefix = "US-INTEL ALERT" if is_us else "IDX-INTEL ALERT"
    message = f"""🚨 *[{brand_prefix}] {category_label.upper()}* 🚨
Emiten: ${ticker.upper()}

{narrative_display}

*Analisis Dampak & Strategi:*
{analysis_display}

*🎯 Rekomendasi : [Class: {rec_label}]*
{rec_display}{horizon_section}{inval_section}{action_section}

{source_display}""".strip()

    return message
