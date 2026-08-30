from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from app.config import get_settings
from app.routers import health_router, monitor_router, webhook_router, chat_router
from app.utils.db_session import engine
from app.utils.logger import get_logger, setup_logging
from app.scheduler import scheduler

settings = get_settings()
setup_logging()
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Application Lifespan context manager.
    Handles startup initialization and graceful shutdown of async database connection pooling.
    """
    logger.info(
        "Starting IDX-Intel AI Service",
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    scheduler.start()
    logger.info("Background scheduler started (cron */5)")
    
    yield
    
    logger.info("Shutting down IDX-Intel AI Service... Closing database pool")
    scheduler.shutdown()
    logger.info("Background scheduler stopped")
    await engine.dispose()
    logger.info("Database pool closed gracefully")


def create_app() -> FastAPI:
    """
    Factory function for FastAPI application instance.
    """
    application = FastAPI(
        title="IDX-Intel AI Enterprise Corporate Action Intelligence Bot",
        description="Autonomous AI Agent Backend for IDX Corporate Action Intelligence & WhatsApp Alerting",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers (Single Responsibility Principle)
    application.include_router(health_router)
    application.include_router(webhook_router)
    application.include_router(monitor_router)
    application.include_router(chat_router)

    @application.get("/", summary="IDX-Intel AI Root Welcome Endpoint")
    async def root_index():
        return JSONResponse(
            status_code=200,
            content={
                "service": "IDX-Intel AI Enterprise Corporate Action Intelligence Bot",
                "version": "2.0.0",
                "edition": "Merah Putih Edition 🇮🇩",
                "demo_dashboard_url": "http://localhost:8045/demo",
                "docs_url": "http://localhost:8045/docs",
                "health_url": "http://localhost:8045/health",
                "waha_dashboard": "http://localhost:3002/dashboard",
            },
        )

    # Resolve robust absolute path for frontend directory
    FRONTEND_DIR = Path("/frontend")
    if not FRONTEND_DIR.exists():
        # Fallback to absolute path based on this file's location (for native local run)
        FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

    @application.get(
        "/demo",
        response_class=HTMLResponse,
        summary="IDX-Intel AI Interactive Merah Putih Demo Dashboard",
    )
    async def serve_demo():
        return FileResponse(FRONTEND_DIR / "index.html")

    @application.get("/index.html", response_class=HTMLResponse)
    async def serve_index_html():
        return FileResponse(FRONTEND_DIR / "index.html")

    @application.get("/demo.html", response_class=HTMLResponse)
    async def serve_demo_html():
        return FileResponse(FRONTEND_DIR / "demo.html")

    @application.get(
        "/connect",
        response_class=HTMLResponse,
        summary="WhatsApp QR Code Connection Page",
    )
    async def serve_connect():
        return FileResponse(FRONTEND_DIR / "connect.html")

    @application.get("/connect.html", response_class=HTMLResponse)
    async def serve_connect_html():
        return FileResponse(FRONTEND_DIR / "connect.html")

    # Mount static files (CSS, JS)
    if FRONTEND_DIR.exists():
        from fastapi.staticfiles import StaticFiles
        application.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
    else:
        print(f"WARNING: Frontend directory not found at {FRONTEND_DIR}")

    return application


app = create_app()
