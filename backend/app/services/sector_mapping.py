import re
from typing import Any

# =====================================================================
# MULTI-MARKET SECTOR TAXONOMY
# 1. COMMODITY SECTORS (Expanded: Tin, Aluminium, Copper, Nickel, Gold, Oil, Coal, etc.)
# 2. S&P 500 & GLOBAL SECTORS (Semis, Big Tech, US Banks, Defense, Macro)
# 3. IDX-IC 11 OFFICIAL SECTORS
# =====================================================================

COMMODITY_TAXONOMY = {
    "tin": {
        "name": "Timah",
        "keywords": ["timah", "tin", "lme-tin", "rkab timah", "smelter timah", "balok timah"],
        "tickers": ["TINS"],
    },
    "aluminium": {
        "name": "Aluminium",
        "keywords": ["aluminium", "aluminum", "lme-alu", "smelter aluminium", "bauxite", "bauksit"],
        "tickers": ["INAI", "ALMI", "ALUM"],
    },
    "copper": {
        "name": "Tembaga",
        "keywords": ["tembaga", "copper", "konsentrat tembaga", "lme-copper", "hg1!", "cper"],
        "tickers": ["AMMN", "MDKA", "CPER", "FCX", "SCCO"],
    },
    "nickel": {
        "name": "Nikel",
        "keywords": ["nikel", "nickel", "lme-nickel", "feronikel", "npi", "baterai nikel", "hpal"],
        "tickers": ["INCO", "ANTM", "NCKL", "MBMA", "NICL", "VALE"],
    },
    "gold_silver": {
        "name": "Logam Mulia",
        "keywords": ["emas", "gold", "xau", "xauusd", "antam emas", "perak", "silver", "xag", "xagusd", "bullion", "safe haven", "gld", "slv"],
        "tickers": ["ANTM", "MDKA", "BRMS", "ARCI", "PSAB", "GLD", "SLV", "XAUUSD", "XAGUSD"],
    },
    "crude_oil": {
        "name": "Minyak Mentah",
        "keywords": ["minyak mentah", "crude oil", "brent", "wti", "opec", "lifting minyak", "harga minyak", "uso"],
        "tickers": ["MEDC", "ENRG", "ELSA", "RUIS", "USO", "BNO", "CL1!", "BRN1!"],
    },
    "coal": {
        "name": "Batu Bara",
        "keywords": ["batu bara", "batubara", "coal", "newcastle", "ici", "dmo batu bara"],
        "tickers": ["ADRO", "PTBA", "ITMG", "BUMI", "BYAN", "INDY", "HRUM", "DOID"],
    },
    "natural_gas": {
        "name": "Gas Alam",
        "keywords": ["gas alam", "natural gas", "lng", "lpg", "pipanisasi gas", "ung"],
        "tickers": ["PGAS", "RAJA", "UNG"],
    },
    "lithium_battery": {
        "name": "Litium & Mineral Baterai",
        "keywords": ["litium", "lithium", "battery metals", "ev battery", "katoda", "lit etf"],
        "tickers": ["ALB", "SQM", "LIT"],
    },
    "uranium_nuclear": {
        "name": "Uranium & Energi Nuklir",
        "keywords": ["uranium", "nuklir", "nuclear energy", "reaktor nuklir", "ura etf"],
        "tickers": ["CCJ", "URA"],
    },
    "cpo": {
        "name": "Kelapa Sawit",
        "keywords": ["cpo", "kelapa sawit", "sawit", "palm oil", "crude palm oil", "biodiesel", "b35", "b40", "mdex"],
        "tickers": ["AALI", "LSIP", "TAPG", "DSNG", "SSMS", "SIMP"],
    },
}

COMMODITY_BENCHMARK_US_ETFS: dict[str, list[str]] = {
    "crude_oil": ["$USO", "$XLE", "$BNO"],
    "natural_gas": ["$UNG"],
    "gold_silver": ["$GLD", "$SLV", "$GDX"],
    "copper": ["$CPER", "$COPX"],
    "nickel": ["$VALE", "$DBB"],
    "tin": ["$DBB"],
    "aluminium": ["$DBB"],
    "coal": ["$XLE", "$AMLP"],
    "lithium_battery": ["$LIT"],
    "uranium_nuclear": ["$URA", "$URNM"],
    "cpo": ["$DBA"],
}

SP500_TAXONOMY = {
    "us_broad_market_etfs": {
        "name": "US Broad Market & Benchmark ETFs",
        "keywords": ["s&p 500", "sp500", "nasdaq", "dow jones", "russell 2000", "wall street", "benchmark index", "broad market"],
        "tickers": ["SPY", "VOO", "QQQ", "DIA", "IWM", "^GSPC", "^IXIC", "^DJI"],
    },
    "us_semiconductors": {
        "name": "US Semiconductors & AI Hardware",
        "keywords": ["semiconductor", "semikonduktor", "chip", "gpu", "ai hardware", "foundry", "wafer", "chipmaker", "smh", "soxx"],
        "tickers": ["NVDA", "TSM", "AMD", "AVGO", "ASML", "QCOM", "INTC", "MU", "SMH", "SOXX"],
    },
    "us_mega_tech": {
        "name": "US Mega Tech & Cloud Platforms",
        "keywords": ["cloud computing", "hyperscaler", "enterprise ai", "software", "cybersecurity", "big tech", "xlk", "xlc"],
        "tickers": ["MSFT", "AAPL", "AMZN", "GOOGL", "GOOG", "META", "CRWD", "PANW", "XLK", "XLC"],
    },
    "us_financials": {
        "name": "US Mega Banks & Financial Services",
        "keywords": ["wall street banks", "investment banking", "net interest income", "credit loss provision", "xlf"],
        "tickers": ["JPM", "BAC", "WFC", "GS", "MS", "C", "XLF"],
    },
    "us_energy": {
        "name": "US Energy & Oil Majors",
        "keywords": ["us energy", "exxonmobil", "chevron", "conocophillips", "xle"],
        "tickers": ["XOM", "CVX", "COP", "SLB", "EOG", "XLE"],
    },
    "us_defense": {
        "name": "US Aerospace & Defense",
        "keywords": ["aerospace", "defense", "military contract", "pentagon", "pertahanan as", "xli"],
        "tickers": ["LMT", "RTX", "BA", "NOC", "GD", "XLI"],
    },
    "us_macro": {
        "name": "US Macro, The Fed & Treasury Yields",
        "keywords": ["cpi", "inflation", "federal reserve", "the fed", "kevin warsh", "donald trump", "trade tariffs", "treasury yield", "bond market", "us dollar", "dxy", "tlt", "uup"],
        "tickers": ["TLT", "UUP", "DXY", "^TNX", "^FVX", "^TYX"],
    },
}

IDX_TAXONOMY = {
    "financials": {
        "name": "Keuangan (Financials - Big Banks)",
        "keywords": ["bank", "perbankan", "kredit", "dpk", "nim", "npl", "bunga pinjaman", "ojk"],
        "tickers": ["BBCA", "BBRI", "BMRI", "BBNI", "BBTN", "BRIS", "BDMN"],
    },
    "energy": {
        "name": "Energi (Energy)",
        "keywords": ["energi", "migas", "eksplorasi migas", "tambang energi"],
        "tickers": ["ADRO", "PTBA", "PGAS", "MEDC", "AKRA", "ITMG", "BUMI"],
    },
    "basic_materials": {
        "name": "Barang Baku (Basic Materials)",
        "keywords": ["barang baku", "industri dasar", "petrokimia", "smelter"],
        "tickers": ["ANTM", "MDKA", "TPIA", "INCO", "AMMN", "BRPT", "INKP"],
    },
    "healthcare": {
        "name": "Kesehatan & Farmasi (Healthcare)",
        "keywords": ["kesehatan", "rumah sakit", "farmasi", "obat", "rawat inap", "bpjs kesehatan"],
        "tickers": ["MIKA", "HEAL", "SILO", "KLBF", "PRDA", "SRAJ"],
    },
    "technology": {
        "name": "Teknologi (Technology)",
        "keywords": ["teknologi", "fintech", "e-commerce", "data center", "startup", "ride hailing"],
        "tickers": ["GOTO", "BUKA", "EMTK", "DCII", "BELI", "WIFI"],
    },
    "infrastructure": {
        "name": "Infrastruktur (Infrastructure & Telco)",
        "keywords": ["infrastruktur", "telekomunikasi", "jalan tol", "menara telekomunikasi", "fiber optik"],
        "tickers": ["TLKM", "ISAT", "EXCL", "TOWR", "TBIG", "JSMR"],
    },
    "consumer_non_cyclical": {
        "name": "Konsumer Primer (Consumer Non-Cyclical / FMCG)",
        "keywords": ["fmcg", "makanan minuman", "sembako", "ritel pangan", "unggas", "poultry"],
        "tickers": ["ICBP", "INDF", "UNVR", "MYOR", "AMRT", "CMRY", "CPIN"],
    },
    "consumer_cyclical": {
        "name": "Konsumer Non-Primer (Consumer Cyclical / Otomotif & Ritel)",
        "keywords": ["otomotif", "kendaraan", "ritel gaya hidup", "elektronik rumah tangga"],
        "tickers": ["ASII", "ACES", "MAPI", "ERAA", "AUTO"],
    },
    "industrials": {
        "name": "Perindustrian (Industrials)",
        "keywords": ["perindustrian", "alat berat", "manufaktur", "komponen"],
        "tickers": ["UNTR", "ARNA", "MARK"],
    },
    "properties": {
        "name": "Properti & Real Estat (Properties)",
        "keywords": ["properti", "real estat", "perumahan", "lahan industri", "marketing sales"],
        "tickers": ["BSDE", "CTRA", "PWON", "SMRA", "ASRI", "DMAS"],
    },
    "transportation": {
        "name": "Transportasi & Logistik (Transportation)",
        "keywords": ["transportasi", "logistik", "pelayaran", "kontainer", "maskapai", "kargo"],
        "tickers": ["SMDR", "TMAS", "GIAA", "ASSA", "BIRD"],
    },
}

GLOBAL_SOURCES = {"YAHOO_FINANCE_REALTIME", "TRADINGVIEW_REALTIME", "CNBC_GLOBAL"}
DOMESTIC_SOURCES = {"IDX_DISCLOSURE", "CNBC_INDONESIA", "KONTAN", "GOOGLE_NEWS"}


def classify_document_to_sectors(
    title: str,
    text: str,
    ticker: str,
    source_name: str | None = None,
) -> list[tuple[str, str, str]]:
    """
    Classifies a news document into one or more sectors across the 3 pillars:
    Returns a list of tuples: (pillar_category, sector_key, sector_display_name)
    where pillar_category is one of: "commodity", "sp500", "idx".

    Enforces strict isolation:
    - Global sources (Yahoo Finance, TradingView, CNBC Global) are never mapped to "idx".
    - Domestic sources (IDX, CNBC ID, Kontan, Google News) are never mapped to "sp500".
    """
    matches: list[tuple[str, str, str]] = []
    combined_content = f"{title} {text} {ticker}".lower()

    # Helper matcher
    def match_item(info: dict[str, Any]) -> bool:
        tickers = info.get("tickers", [])
        if ticker.upper() in [t.upper() for t in tickers]:
            return True
        for t in tickers:
            if re.search(r"\b" + re.escape(t.lower()) + r"\b", combined_content):
                return True
        for kw in info.get("keywords", []):
            if re.search(r"\b" + re.escape(kw) + r"\b", combined_content):
                return True
        return False

    # 1. Check Commodity Taxonomy (Always evaluated across domestic & global)
    for key, info in COMMODITY_TAXONOMY.items():
        if match_item(info):
            matches.append(("commodity", key, info["name"]))

    # 2. Check S&P 500 Taxonomy (Only if not strictly a domestic source)
    if source_name not in DOMESTIC_SOURCES:
        for key, info in SP500_TAXONOMY.items():
            if match_item(info):
                matches.append(("sp500", key, info["name"]))

    # 3. Check IDX Taxonomy (Only if not strictly a global source)
    if source_name not in GLOBAL_SOURCES:
        for key, info in IDX_TAXONOMY.items():
            if match_item(info):
                matches.append(("idx", key, info["name"]))

    return matches
