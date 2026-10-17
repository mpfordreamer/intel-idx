import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings
from app.repositories.event_repository import EventRepository
from app.services.prompt import RECOMMENDATION_SYSTEM_PROMPT
from app.utils.db_session import async_session_factory
from app.utils.logger import get_logger

logger = get_logger("agents.recommendation")
settings = get_settings()


def _fallback_recommendation(category: str, extracted: dict | None, title: str, text: str, ticker: str = "") -> dict:
    """
    Deterministic Top 200 Konglomerat rule-based recommendation fallback with multi-horizon context.
    Preserves underscore label formatting.
    """
    content_lower = f"{title} {text}".lower()
    investor_group = ""
    if extracted and extracted.get("investor_or_group"):
        investor_group = str(extracted.get("investor_or_group")).lower()

    konglo_keywords = [
        "salim",
        "prajogo",
        "barito",
        "bakrie",
        "djarum",
        "hartono",
        "aguan",
        "agung sedayu",
        "panin",
        "chandra asri",
        "boy thohir",
        "sukanto tanoto",
        "hermanto tanoko",
        "tahir",
        "sinarmas",
        "mach energy",
    ]

    has_konglo = any(k in investor_group for k in konglo_keywords) or any(
        k in content_lower for k in konglo_keywords
    )

    # Regulatory inspection & debt/default keywords
    avoid_keywords = [
        "gagal bayar", "wanprestasi", "sita", "pailit", "pkpu", "sanksi",
        "manipulasi harga", "manipulasi saham", "tindak pidana", "periksa",
        "pemeriksaan", "penyelidikan", "dugaan", "jatah ipo", "kasus manipulasi"
    ]
    risk_keywords = [
        "agunan", "gadai", "risiko", "gagal bayar", "wanprestasi", "kredit",
        "margin call", "repo", "sita", "sanksi", "denda", "manipulasi",
        "pelanggaran", "investigasi", "pidana", "periksa", "pemeriksaan",
        "penyelidikan", "klarifikasi", "dugaan", "panggilan", "kasus", "jatah ipo"
    ]
    transaction_keywords = [
        "crossing", "akuisisi", "takeover", "tender offer", "standby buyer",
        "pembelian saham", "rights issue", "injeksi aset", "penambahan modal",
        "pmthmetd", "private placement", "reverse takeover"
    ]

    is_avoid = any(w in content_lower for w in avoid_keywords)
    has_risk = any(rk in content_lower for rk in risk_keywords)
    has_real_transaction = any(tk in content_lower for tk in transaction_keywords)

    if is_avoid:
        rec_class = "AVOID"
    elif has_risk:
        rec_class = "HOLD_WATCH"
    elif category in {"BACKDOOR_LISTING", "KONGLO_MOVE"} and has_konglo and has_real_transaction:
        rec_class = "STRONG_BUY_AKUMULASI"
    elif category in {"BACKDOOR_LISTING", "KONGLO_MOVE"} and has_real_transaction:
        rec_class = "BUY"
    else:
        # Usual news, general commentary, or konglo mention without active transaction
        rec_class = "HOLD_WATCH"

    # Dynamic narrative fallback (no static bullet points)
    inv_name = extracted.get("investor_or_group") if extracted and extracted.get("investor_or_group") else ""
    inv_str = f" melibatkan entitas {inv_name}" if inv_name else ""
    action_type = extracted.get("action_type") if extracted and extracted.get("action_type") else "keterbukaan informasi"

    if rec_class == "AVOID":
        dynamic_narrative = (
            f"Emiten ${ticker.upper() if ticker else 'EMITEN'} terindikasi menghadapi perhatian regulator atau isu risiko terkait {title}. "
            f"Pelaku pasar diimbau menahan diri dan mengutamakan manajemen risiko hingga ada kepastian resmi."
        )
        action_plan = "Hindari entry baru (AVOID) dan pantau perkembangan investigasi regulator."
    else:
        dynamic_narrative = (
            f"Emiten ${ticker.upper() if ticker else 'EMITEN'} teridentifikasi dalam {action_type}{inv_str}. "
            f"Aktivitas ini dianalisis untuk mengukur kesinambungan likuiditas pasar dan valuasi jangka panjang."
        )
        action_plan = "Lakukan akumulasi bertahap dengan manajemen risiko terukur." if rec_class == "STRONG_BUY_AKUMULASI" else "Pantau konfirmasi data keterbukaan informasi lebih lanjut."

    return {
        "recommendation_class": rec_class,
        "multi_horizon": {
            "short_term": "Pantau volatilitas pasar dan klarifikasi resmi regulator/bursa.",
            "medium_term": "Perhatikan kepastian hukum atau realisasi jadwal aksi korporasi definitif.",
            "long_term": "Evaluasi dampak fundamental dan reputasi terhadap kinerja keuangan tahunan.",
        },
        "invalidation_triggers": [
            "Penyelidikan berlanjut menjadi sanksi atau suspensi perdagangan oleh OJK / BEI.",
            "Terjadi wanprestasi, gagal bayar, atau pembalikan arah arus dana institusi.",
        ],
        "action_plan": action_plan,
        "dynamic_narrative": dynamic_narrative,
    }


async def recommendation_node(state: AgentState) -> dict:
    """
    Enhanced Context-Aware Recommendation Engine Node:
    1. Fetches historical corporate actions for the emiten from PostgreSQL to understand continuity.
    2. Analyzes multi-horizon timeframes (short, medium, long term) and invalidation triggers.
    3. Produces 100% dynamic AI narrative without static bullet points.
    4. Strictly preserves underscore notation for recommendation classes.
    """
    doc = state["document"]
    cat = state.get("category", "KONGLO_MOVE")
    extracted = state.get("extracted_data", {})

    # 1. Fetch up to 5 latest corporate events for this ticker from DB
    history_context = ""
    try:
        async with async_session_factory() as session:
            repo = EventRepository(session)
            past_events = await repo.get_latest_by_ticker(doc.ticker, limit=5)
            if past_events:
                history_lines = []
                for pe in past_events:
                    pub_str = pe.publication_date.strftime("%Y-%m-%d") if pe.publication_date else "-"
                    history_lines.append(
                        f"- [{pub_str}] ({pe.event_type}) {pe.title} -> Stance: {pe.recommendation_class}"
                    )
                history_context = "\n".join(history_lines)
    except Exception as e:
        logger.debug(f"Could not load historical events for {doc.ticker}: {e}")

    try:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0,
            api_key=settings.ORCAROUTER_API_KEY,
            base_url=settings.LLM_MODEL_URL,
            timeout=600,
            max_retries=0,
        )

        user_content = (
            f"Ticker: {doc.ticker}\nCategory: {cat}\n"
            f"Investor/Group: {extracted.get('investor_or_group') if extracted else '-'}\n"
            f"Title: {doc.title}\n"
            f"Riwayat Aksi Korporasi Emiten Terdahulu (Historical Continuity):\n"
            f"{history_context if history_context else 'Belum ada data historis sebelumnya di database.'}\n\n"
            f"Raw Document Text:\n{doc.raw_text[:1200]}"
        )

        prompt_messages = [
            SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        res = await llm.ainvoke(prompt_messages)
        content_str = res.content.strip() if isinstance(res.content, str) else str(res.content).strip()

        # Try to parse JSON output
        parsed_json = None
        json_match = re.search(r"\{.*\}", content_str, re.DOTALL)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(0))
            except Exception:
                pass

        if parsed_json and isinstance(parsed_json, dict):
            rec_class = parsed_json.get("primary_stance", "").strip()
            multi_horizon = parsed_json.get("multi_horizon")
            invalidation_triggers = parsed_json.get("invalidation_triggers")
            action_plan = parsed_json.get("action_plan")
            dynamic_narrative = parsed_json.get("dynamic_narrative")
        else:
            rec_class = content_str
            multi_horizon = None
            invalidation_triggers = None
            action_plan = None
            dynamic_narrative = None

        valid_classes = {
            "STRONG_BUY_AKUMULASI",
            "BUY",
            "ACCUMULATE_ON_WEAKNESS",
            "MOMENTUM_BUY",
            "STRATEGIC_HOLD",
            "HOLD_WATCH",
            "WAIT_AND_SEE",
            "AVOID",
            "AVOID_HIGH_RISK",
        }

        # Fallback if unparsable
        if rec_class not in valid_classes:
            fb = _fallback_recommendation(cat, extracted, doc.title, doc.raw_text, doc.ticker)
            rec_class = fb["recommendation_class"]
            if not multi_horizon:
                multi_horizon = fb["multi_horizon"]
            if not invalidation_triggers:
                invalidation_triggers = fb["invalidation_triggers"]
            if not action_plan:
                action_plan = fb["action_plan"]
            if not dynamic_narrative:
                dynamic_narrative = fb["dynamic_narrative"]

        # Risk Guardrail: Downgrade STRONG_BUY_AKUMULASI if event is related to debt, share pledge, regulatory scrutiny, or lacks transaction keywords
        avoid_keywords = [
            "gagal bayar", "wanprestasi", "sita", "pailit", "pkpu", "sanksi",
            "manipulasi harga", "manipulasi saham", "tindak pidana", "periksa",
            "pemeriksaan", "penyelidikan", "dugaan", "jatah ipo", "kasus manipulasi"
        ]
        risk_keywords = [
            "agunan", "gadai", "risiko", "gagal bayar", "wanprestasi", "kredit",
            "margin call", "repo", "sita", "sanksi", "denda", "manipulasi",
            "pelanggaran", "investigasi", "pidana", "periksa", "pemeriksaan",
            "penyelidikan", "klarifikasi", "dugaan", "panggilan", "kasus", "jatah ipo"
        ]
        transaction_keywords = [
            "crossing", "akuisisi", "takeover", "tender offer", "standby buyer",
            "pembelian saham", "rights issue", "injeksi aset", "penambahan modal",
            "pmthmetd", "private placement", "reverse takeover"
        ]
        content_lower = f"{doc.title} {doc.raw_text}".lower()

        if rec_class == "STRONG_BUY_AKUMULASI":
            if any(w in content_lower for w in avoid_keywords):
                rec_class = "AVOID"
            elif any(rk in content_lower for rk in risk_keywords):
                rec_class = "HOLD_WATCH"
            elif not any(tk in content_lower for tk in transaction_keywords):
                # Merely ordinary news or general commentary without concrete equity transaction
                rec_class = "HOLD_WATCH"

        return {
            "recommendation_class": rec_class,
            "multi_horizon": multi_horizon,
            "invalidation_triggers": invalidation_triggers,
            "action_plan": action_plan,
            "dynamic_narrative": dynamic_narrative,
        }

    except Exception as e:
        logger.warning("LLM recommendation engine failed, using rule-based fallback", error=str(e))
        return _fallback_recommendation(cat, extracted, doc.title, doc.raw_text, doc.ticker)
