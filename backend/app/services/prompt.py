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
   - A previously loss-making company for years suddenly generates a net profit (turnaround).
   - Net profit skyrockets unnaturally or exceeds expectations (e.g., increases >200% YoY).

4. "BIG_CONTRACT":
   - The company wins a tender, new project, or joint venture with a fantastic value (approaching or exceeding the company's own Market Cap, e.g., > 50 Billion Rupiah or equivalent in USD).

5. "IRRELEVANT":
   - Routine corporate action news: Ordinary Rights Issue without conglomerate standby buyers, ordinary Dividend Distribution, routine Financial Reports, ordinary UMA / Suspension unrelated to accumulation, or general news not involving Backdoor Listing / Smart Money Accumulation.

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
- investor_or_group: Identify the specific Konglomerat, Smart Money, or Investor Group involved (e.g., "Mach Energy (Grup Salim)", "Grup Barito / Prajogo Pangestu", "Grup Bakrie", "Hermanto Tanoko")
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
# 4. RECOMMENDATION ENGINE SYSTEM PROMPT (Top 200 Konglomerat Rule)
# =====================================================================
RECOMMENDATION_SYSTEM_PROMPT = """
You are an Investment Strategy Engine for IDX stocks.
Determine the final recommendation class STRICTLY based on these rules:

1. "STRONG_BUY_AKUMULASI":
   - MANDATORY when the corporate action involves Top 200 Konglomerat Indonesia or famous business groups (e.g., Prajogo Pangestu / Grup Barito, Salim Group, Djarum, Bakrie, Agung Sedayu, Panin, Chandra Asri, Boy Thohir, Sukanto Tanoto, Franky Widjaja, Tomy Winata, Hermanto Tanoko, Dato Sri Tahir, Sinarmas, Happy Hapsoro etc.).
   - MANDATORY for Reverse Takeovers / Backdoor Listing backed by tier-1 Smart Money.

2. "BUY":
   - Positive corporate action with strategic expansion or debt reduction without tier-1 Konglomerat participation.

3. "HOLD_WATCH":
   - Speculative corporate action, early-stage rumor, or neutral valuation impact.

4. "AVOID":
   - Dilutive corporate action without standby buyer or negative restructuring.

Output ONLY the exact recommendation class string: STRONG_BUY_AKUMULASI, BUY, HOLD_WATCH, or AVOID.
""".strip()


# =====================================================================
# 5. WHATSAPP MARKDOWN ALERT FORMATTER
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
) -> str:
    """
    Formats extracted intelligence into the crisp, visually stunning WhatsApp markdown template
    required by IDX-Intel AI user specifications.
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

    # Category and event parsing
    category_label = "Konglo Move / Akumulasi Strategis"
    if event_type == "BACKDOOR_LISTING":
        category_label = "Backdoor Listing / Injeksi Aset"
    elif event_type == "SURPRISE_FUNDAMENTAL":
        category_label = "Surprise Fundamental / Laba Meroket"
    elif event_type == "BIG_CONTRACT":
        category_label = "Big Contract / Proyek Jumbo"

    action_type = "Corporate Action"
    investor_group = ""
    
    details = []

    if extracted_data:
        action_type = extracted_data.get("action_type") or "Corporate Action"
        investor_group = extracted_data.get("investor_or_group")
        if investor_group:
            investor_group = f" yang melibatkan {investor_group}"
        else:
            investor_group = ""
            
        price_val = extracted_data.get("execution_price_idr")
        if price_val:
            details.append(f"dieksekusi di harga Rp {price_val:,.0f} per saham".replace(",", "."))
            
        val_idr = extracted_data.get("transaction_value_idr")
        if val_idr:
            if val_idr >= 1_000_000_000_000:
                tx_val_format = f"± Rp {val_idr / 1_000_000_000_000:.2f} Triliun".replace(".", ",")
            elif val_idr >= 1_000_000_000:
                tx_val_format = f"± Rp {val_idr / 1_000_000_000:.2f} Miliar".replace(".", ",")
            else:
                tx_val_format = f"Rp {val_idr:,.0f}".replace(",", ".")
            details.append(f"dengan total nilai mencapai {tx_val_format}")
            
        owner_val = extracted_data.get("ownership_percentage")
        if owner_val:
            details.append(f"yang merepresentasikan kepemilikan saham sebesar {owner_val:.1f}%")

    if details:
        corporate_detail = ", ".join(details) + "."
    else:
        corporate_detail = "tanpa ada rincian transaksi eksplisit yang disebutkan."

    # Recommendation processing
    rec_label = recommendation_class or "HOLD WATCH"
    rec_label = rec_label.replace("_", " ")  # Remove underscores!
    
    if "STRONG BUY" in rec_label or "AKUMULASI" in rec_label:
        rec_display = f"💡 {rec_label} — Didukung oleh pergerakan tier-1 konglomerat / prospek ekspansi kuat."
    elif "BUY" in rec_label:
        rec_display = f"📈 {rec_label} — Transaksi positif dengan ekspansi fundamental yang solid."
    elif "HOLD" in rec_label:
        rec_display = f"🔎 {rec_label} — Pantau realisasi likuiditas pasar terlebih dahulu."
    else:
        rec_display = f"⚠️ {rec_label} — Evaluasi kembali risiko terkait."

    analysis_display = impact_analysis or "Analisis dampak sedang diproses."
    source_display = f"Sumber Berita: {source_url}" if source_url else ""

    message = f"""🚨 *[IDX-INTEL ALERT] {category_label.upper()}* 🚨
Emiten: ${ticker.upper()}

Telah terdeteksi aktivitas {action_type}{investor_group}, {corporate_detail}
Kategori pergerakan ini diidentifikasi sebagai indikasi {category_label}.

*Analisis Dampak & Strategi:*
{analysis_display}

*Rekomendasi Keputusan:*
*{rec_display}*

{source_display}""".strip()

    return message
