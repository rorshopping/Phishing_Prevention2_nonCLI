"""AI-SEO / LLM visibility files (llms.txt, llms-full.txt, robots.txt).

Pure file-reading helpers so the content can be tested without importing
the full FastAPI application. The FastAPI routes in src/main.py delegate here.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_FALLBACK_ROBOTS = """User-agent: *
Allow: /
"""


def _read(name: str) -> str:
    path = REPO_ROOT / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def get_llms_txt() -> str:
    return _read("llms.txt")


def get_llms_full_txt() -> str:
    return _read("llms-full.txt")


def get_robots_txt() -> str:
    robots = REPO_ROOT / "static" / "robots.txt"
    return robots.read_text(encoding="utf-8") if robots.exists() else _FALLBACK_ROBOTS
