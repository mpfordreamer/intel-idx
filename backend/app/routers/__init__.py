from app.routers.health import router as health_router
from app.routers.webhook import router as webhook_router
from app.routers.monitor import router as monitor_router
from app.routers.chat import router as chat_router
from app.routers.call import router as call_router
from app.routers.sectors import router as sector_router
from app.routers.idx import router as idx_router
from app.routers.us import router as us_router
from app.routers.macro import router as macro_router

__all__ = [
    "health_router",
    "webhook_router",
    "monitor_router",
    "chat_router",
    "call_router",
    "sector_router",
    "idx_router",
    "us_router",
    "macro_router",
]
