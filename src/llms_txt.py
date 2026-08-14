"""AI-SEO / LLM visibility files (llms.txt, llms-full.txt, robots.txt).

Pure file-reading helpers so the content can be tested without importing
the full FastAPI application. The FastAPI routes in src/main.py delegate here.

All files are read from ``static/`` — the single source of truth that is
mirrored byte-for-byte to the repo root (served by Vercel), so the FastAPI
routes and the deployed root expose identical content.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = REPO_ROOT / "static"

_FALLBACK_ROBOTS = """User-agent: *
Allow: /
"""


def _read(name: str) -> str:
    path = STATIC_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def get_llms_txt() -> str:
    return _read("llms.txt")


def get_llms_full_txt() -> str:
    return _read("llms-full.txt")


def get_robots_txt() -> str:
    return _read("robots.txt") or _FALLBACK_ROBOTS
