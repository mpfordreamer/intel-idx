import json
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger("agents.chat")
settings = get_settings()

CHAT_SYSTEM_PROMPT = """Anda adalah asisten AI dari IDX-Intel, khusus memberikan analisis pergerakan saham dan aksi korporasi strategis (termasuk saham konglomerasi) di Bursa Efek Indonesia (BEI).
Anda akan diberikan data historis aksi korporasi terbaru dari suatu emiten atau kelompok emiten.
Tugas Anda adalah merangkai data tersebut menjadi satu balasan WhatsApp yang analitis, menarik, mengalir, dan tidak monoton.
Gunakan format Markdown WhatsApp (bold dengan *, italic dengan _).
Gunakan bahasa Indonesia yang profesional namun mudah dipahami investor retail.

Aturan Penting:
1. Jika tidak ada event yang signifikan, sampaikan bahwa emiten saat ini cenderung sepi dari aksi strategis, namun sebutkan event terakhir jika ada.
2. Jika ada indikasi masuknya investor besar, private placement, akuisisi, atau RUPSLB penting, tegaskan dampaknya terhadap prospek emiten.
3. Jangan pernah mengarang data (halusinasi). Analisis HANYA berdasarkan data event yang diberikan.
4. Buatlah kesimpulan (1 kalimat) di akhir pesan (contoh: "Kesimpulan: ...").
"""

class ChatAgentService:
    @classmethod
    def _get_llm(cls):
        """Returns the LLM configured with temperature 0.5."""
        if settings.LLM_PROVIDER == "orcarouter":
            # For local Ollama, use ChatOllama which supports num_ctx natively
            # to prevent DeepSeek 128k context allocation OOM
            return ChatOllama(
                model=settings.LLM_MODEL,
                temperature=0.5,
                base_url=settings.LLM_MODEL_URL.replace("/v1", ""),
                num_ctx=4096,
                timeout=600,
                max_retries=2
            )
        
        # Fallback for explicit OpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.5,
            api_key=settings.ORCAROUTER_API_KEY,
            base_url=settings.LLM_MODEL_URL,
            timeout=600,
            max_retries=2
        )

    @classmethod
    async def generate_ticker_summary(cls, ticker: str, events: List[Dict[str, Any]]) -> str:
        """Generates a dynamic WhatsApp summary for a specific ticker."""
        logger.info(f"Generating dynamic summary for {ticker} with {len(events)} events.")
        llm = cls._get_llm()
        
        events_str = json.dumps(events, indent=2, ensure_ascii=False)
        
        prompt = [
            SystemMessage(content=CHAT_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Buatkan ringkasan analisis untuk emiten: *{ticker.upper()}*.\n"
                        f"Berikut adalah data aksi korporasi / event terbarunya:\n{events_str}\n\n"
                        f"Tolong rangkum dampaknya dalam 2-3 paragraf singkat yang cocok untuk dikirim via WhatsApp."
            )
        ]
        
        try:
            res = await llm.ainvoke(prompt)
            content = res.content if isinstance(res.content, str) else str(res.content)
            return content.strip()
        except Exception as e:
            logger.error(f"Failed to generate dynamic summary for {ticker}", error=str(e))
            # Fallback
            if events:
                latest = events[0]
                return f"⚠️ [Sistem Sibuk]\nEmiten: *${ticker.upper()}*\nEvent Terakhir: {latest.get('title', 'N/A')}\n\n_Mohon coba lagi nanti untuk analisis AI._"
            return f"ℹ️ Belum ada aksi korporasi strategis atau Konglo Move yang tercatat untuk *${ticker.upper()}*."

    @classmethod
    async def generate_category_summary(cls, category_name: str, events: List[Dict[str, Any]]) -> str:
        """Generates a dynamic WhatsApp summary for a specific category (e.g. Konglo Move, Famous Stocks)."""
        logger.info(f"Generating dynamic category summary for {category_name} with {len(events)} events.")
        llm = cls._get_llm()
        
        events_str = json.dumps(events, indent=2, ensure_ascii=False)
        
        prompt = [
            SystemMessage(content=CHAT_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Buatkan ringkasan pergerakan untuk kelompok: *{category_name}*.\n"
                        f"Berikut adalah data aksi korporasi / event terbarunya:\n{events_str}\n\n"
                        f"Sebutkan ticker-ticker yang terlibat, apa aksinya, dan apa potensi sentimen pasarnya. Rangkum dalam format poin-poin yang enak dibaca via WhatsApp."
            )
        ]
        
        try:
            res = await llm.ainvoke(prompt)
            content = res.content if isinstance(res.content, str) else str(res.content)
            return content.strip()
        except Exception as e:
            logger.error(f"Failed to generate dynamic category summary for {category_name}", error=str(e))
            # Fallback
            if events:
                lines = [f"⚠️ [Sistem Sibuk] - Pergerakan *{category_name}* Terakhir:"]
                for ev in events[:5]:
                    lines.append(f"- *${ev.get('ticker')}*: {ev.get('title', 'N/A')}")
                return "\n".join(lines)
            return f"ℹ️ Saat ini belum ada pergerakan terbaru untuk kategori *{category_name}*."
