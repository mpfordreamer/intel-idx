from fastapi import APIRouter
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger("routers.chat")

router = APIRouter(prefix="/api/v1", tags=["Chatbot"])

# Initialize Ollama model
chat_model = ChatOllama(
    model="qwen3:14b",
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0.3
)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat", summary="Customer Service AI Chatbot")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received chat message: {request.message}")
    
    # System prompt directing the AI to be a Customer Service bot
    # It can respond in English or Indonesian depending on the user input.
    system_prompt = (
        "You are 'IDX-Intel AI', a helpful and professional customer service chatbot "
        "for the 'Ternak Saham' community and the IDX-Intel AI platform. "
        "Your role is to assist users with questions about the stock market, our AI features, "
        "and general inquiries. "
        "IMPORTANT: You can respond in either English or Indonesian, depending on the language "
        "the user uses in their message. Match their language naturally. Keep your answers concise, "
        "informative, and friendly."
    )
    
    try:
        sys_msg = SystemMessage(content=system_prompt)
        user_msg = HumanMessage(content=request.message)
        
        response = chat_model.invoke([sys_msg, user_msg])
        reply_text = response.content
        
        # Strip <think> tags
        import re
        reply_text = re.sub(r'<think>.*?</think>', '', reply_text, flags=re.DOTALL).strip()
        
        return {"success": True, "reply": reply_text}
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return {"success": False, "reply": "Maaf, sistem AI sedang mengalami gangguan. Silakan coba lagi nanti."}
