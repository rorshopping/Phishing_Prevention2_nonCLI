import asyncio
import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings
from src.database.session import engine
from src.database.session import Base
from src.api import clients, campaigns, webhooks, vishing, risk, training, reports, templates, contact
from src.agents.orchestrator import Orchestrator

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("phishguard")

app = FastAPI(title="PhishDefend AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(campaigns.router)
app.include_router(webhooks.router)
app.include_router(vishing.router)
app.include_router(risk.router)
app.include_router(training.router)
app.include_router(reports.router)
app.include_router(templates.router)
app.include_router(contact.router)

_orchestrator: Orchestrator | None = None
_scheduler_task: asyncio.Task | None = None


async def _scheduler_loop():
    global _orchestrator
    _orchestrator = Orchestrator()
    interval = settings.scheduler_interval_seconds
    logger.info("Background scheduler started (interval=%ds)", interval)
    while True:
        try:
            await _orchestrator.monitor_all_active_campaigns()
        except Exception:
            logger.exception("Scheduler monitoring error")
        try:
            await _orchestrator.run_scheduled_campaigns()
        except Exception:
            logger.exception("Scheduler campaign launch error")
        await asyncio.sleep(interval)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if not already present)")

    if settings.gophish_api_key:
        global _scheduler_task
        _scheduler_task = asyncio.create_task(_scheduler_loop())
        logger.info("Background scheduler started")
    else:
        logger.warning("No GOPHISH_API_KEY set — scheduler disabled")


@app.on_event("shutdown")
async def on_shutdown():
    if _scheduler_task:
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
    await engine.dispose()
    logger.info("Engine disposed")


@app.get("/health")
async def health():
    db_ok = False
    gophish_ok = False
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass
    if settings.gophish_api_key:
        try:
            import httpx
            async with httpx.AsyncClient(verify=False) as hc:
                resp = await hc.get(f"{settings.gophish_api_url}/campaigns/",
                    headers={"Authorization": f"Bearer {settings.gophish_api_key}"}, timeout=5)
                gophish_ok = resp.status_code < 500
        except Exception:
            pass
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "phishguard",
        "database": "connected" if db_ok else "error",
        "gophish": "reachable" if gophish_ok else "unreachable",
        "scheduler": _scheduler_task is not None and not _scheduler_task.done(),
    }


STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)


# ---------- legal pages (served as HTML) ----------

def _read_static(name: str) -> str:
    path = STATIC_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


LEGAL_PAGES = {
    "impressum": _read_static("impressum.html"),
    "privacy": _read_static("privacy.html"),
    "data-processing-agreement": _read_static("dpa.html"),
}


@app.get("/impressum", response_class=HTMLResponse)
async def impressum_page():
    html = LEGAL_PAGES.get("impressum")
    if not html:
        return HTMLResponse("<h1>Impressum</h1><p>Coming soon.</p>", status_code=200)
    return HTMLResponse(html)


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page():
    html = LEGAL_PAGES.get("privacy")
    if not html:
        return HTMLResponse("<h1>Privacy Policy</h1><p>Coming soon.</p>", status_code=200)
    return HTMLResponse(html)


@app.get("/data-processing-agreement", response_class=HTMLResponse)
async def dpa_page():
    html = LEGAL_PAGES.get("data-processing-agreement")
    if not html:
        return HTMLResponse("<h1>Data Processing Agreement</h1><p>Coming soon.</p>", status_code=200)
    return HTMLResponse(html)


# ---------- SEO / indexing ----------

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return """User-agent: *
Allow: /
Sitemap: https://phishdefend-ai.vercel.app/sitemap.xml
"""


@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap_xml():
    now = "2026-07-30"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url><loc>https://phishdefend-ai.vercel.app/</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://phishdefend-ai.vercel.app/impressum</loc><lastmod>{now}</lastmod><changefreq>monthly</changefreq><priority>0.3</priority></url>
  <url><loc>https://phishdefend-ai.vercel.app/privacy</loc><lastmod>{now}</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>
  <url><loc>https://phishdefend-ai.vercel.app/data-processing-agreement</loc><lastmod>{now}</lastmod><changefreq>monthly</changefreq><priority>0.4</priority></url>
</urlset>
"""


# ---------- static frontend ----------

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


# ---------- error handlers ----------

_404_HTML = _read_static("404.html") or "<h1>404 Not Found</h1>"


@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc):
    if exc.status_code == 404:
        return HTMLResponse(_404_HTML, status_code=404)
    return await http_exception_handler(request, exc)


# ---------- middleware ----------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    logger.info(
        "%s %s -> %s (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response
