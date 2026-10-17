import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from app.config import get_settings
from app.routers import (
    health_router,
    monitor_router,
    webhook_router,
    chat_router,
    call_router,
    sector_router,
    idx_router,
    us_router,
    macro_router,
)
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
    
    # Start the dedicated queue worker
    from app.scheduler import _document_queue_worker
    app.state.queue_worker_task = asyncio.create_task(_document_queue_worker())
    
    scheduler.start()
    logger.info("Background scheduler started (cron */5)")
    
    yield
    
    logger.info("Shutting down IDX-Intel AI Service... Closing database pool")
    scheduler.shutdown()
    if hasattr(app.state, "queue_worker_task"):
        app.state.queue_worker_task.cancel()
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
    application.include_router(call_router)
    application.include_router(sector_router)
    application.include_router(idx_router)
    application.include_router(us_router)
    application.include_router(macro_router)

    # Resolve robust absolute path for frontend directory
    FRONTEND_DIR = Path("/frontend")
    if not FRONTEND_DIR.exists():
        # Fallback to absolute path based on this file's location (for native local run)
        FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

    NO_CACHE_HEADERS = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"}

    @application.get("/", summary="IDX-Intel AI Root Welcome Endpoint")
    async def root_index(request: Request):
        if "text/html" in request.headers.get("accept", "") and (FRONTEND_DIR / "index.html").exists():
            return FileResponse(FRONTEND_DIR / "index.html", headers=NO_CACHE_HEADERS)
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

    @application.get(
        "/demo",
        response_class=HTMLResponse,
        summary="IDX-Intel AI Interactive Merah Putih Demo Dashboard",
    )
    async def serve_demo():
        return FileResponse(FRONTEND_DIR / "demo.html", headers=NO_CACHE_HEADERS)

    @application.get("/demo.html", response_class=HTMLResponse)
    async def serve_demo_html():
        return FileResponse(FRONTEND_DIR / "demo.html", headers=NO_CACHE_HEADERS)

    @application.get("/index.html", response_class=HTMLResponse)
    async def serve_index_html():
        return FileResponse(FRONTEND_DIR / "index.html", headers=NO_CACHE_HEADERS)

    @application.get(
        "/connect",
        response_class=HTMLResponse,
        summary="WhatsApp QR Code Connection Page",
    )
    async def serve_connect():
        return FileResponse(FRONTEND_DIR / "connect.html", headers=NO_CACHE_HEADERS)

    @application.get("/connect.html", response_class=HTMLResponse)
    async def serve_connect_html():
        return FileResponse(FRONTEND_DIR / "connect.html", headers=NO_CACHE_HEADERS)

    # Static Assets Direct & Fallback Serving (Resolves 404 on relative paths ./style.css and ./i18n.js)
    @application.get("/style.css", summary="Serve Frontend CSS")
    @application.get("/{prefix}/style.css", summary="Serve Frontend CSS with Prefix Fallback")
    async def serve_style_css(prefix: str = ""):
        css_file = FRONTEND_DIR / "style.css"
        if css_file.exists():
            return FileResponse(css_file, media_type="text/css", headers=NO_CACHE_HEADERS)
        return JSONResponse(status_code=404, content={"detail": "style.css not found"})

    @application.get("/i18n.js", summary="Serve Frontend i18n JavaScript")
    @application.get("/{prefix}/i18n.js", summary="Serve Frontend i18n JavaScript with Prefix Fallback")
    async def serve_i18n_js(prefix: str = ""):
        js_file = FRONTEND_DIR / "i18n.js"
        if js_file.exists():
            return FileResponse(js_file, media_type="application/javascript", headers=NO_CACHE_HEADERS)
        return JSONResponse(status_code=404, content={"detail": "i18n.js not found"})

    @application.get("/favicon.ico", include_in_schema=False)
    async def serve_favicon():
        fav = FRONTEND_DIR / "favicon.ico"
        if fav.exists():
            return FileResponse(fav, headers=NO_CACHE_HEADERS)
        return JSONResponse(status_code=204, content={})

    # Mount static files (CSS, JS)
    if FRONTEND_DIR.exists():
        from fastapi.staticfiles import StaticFiles
        application.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
    else:
        print(f"WARNING: Frontend directory not found at {FRONTEND_DIR}")

    return application


app = create_app()
