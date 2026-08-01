import logging
from typing import Any

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class PersonalizationError(Exception):
    pass


SERPAPI_BASE = "https://serpapi.com/search"


async def search_employee_data(
    employee_name: str,
    company_name: str,
    *,
    force_refresh: bool = False,
) -> dict[str, Any]:
    if not settings.serpapi_api_key:
        logger.warning("SERPAPI_API_KEY not set; returning empty employee data")
        return {"role": "", "linkedin_url": "", "recent_news": ""}

    cache_key = (employee_name.lower(), company_name.lower())

    if not force_refresh:
        result = _get_cached(cache_key)
        if result is not None:
            logger.debug("Cache hit for %s @ %s", employee_name, company_name)
            return result

    params: dict[str, str] = {
        "api_key": settings.serpapi_api_key,
        "q": f"{employee_name} {company_name}",
        "engine": "google",
        "num": "5",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(SERPAPI_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error("SerpAPI HTTP error: %s", e)
            raise PersonalizationError(f"SerpAPI request failed: {e}") from e
        except httpx.RequestError as e:
            logger.error("SerpAPI network error: %s", e)
            raise PersonalizationError(f"SerpAPI network error: {e}") from e

    result = _parse_search_results(employee_name, company_name, data)
    _set_cache(cache_key, result)
    return result


def _parse_search_results(
    employee_name: str,
    company_name: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    role = ""
    linkedin_url = ""
    recent_news: list[str] = []

    organic = data.get("organic_results", [])
    for item in organic:
        link = item.get("link", "")
        snippet = item.get("snippet", "")

        if "linkedin.com/in/" in link:
            linkedin_url = link.split("?")[0]
            if not role and snippet:
                role = snippet.split("·")[0].strip() if "·" in snippet else ""

        if _is_news_item(item):
            recent_news.append(snippet or item.get("title", ""))

        if not role and snippet:
            for kw in (" at ", " bei ", "@ ", " - "):
                if kw in snippet:
                    role = snippet.split(kw)[0].strip()
                    break

    return {
        "role": role,
        "linkedin_url": linkedin_url,
        "recent_news": " | ".join(recent_news[:3]),
    }


def _is_news_item(item: dict[str, Any]) -> bool:
    return bool(item.get("news_token") or "news" in item.get("type", "").lower() or
                item.get("source") in ("news", "News"))


def build_target_context(employee: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": employee.get("name", ""),
        "role": employee.get("role", ""),
        "department": employee.get("department", ""),
        "group": employee.get("group", "general"),
        "linkedin_url": employee.get("linkedin_url", ""),
        "public_data": employee.get("public_data") or {},
    }


def enrich_with_search(
    employee: dict[str, Any],
    search_result: dict[str, Any],
) -> dict[str, Any]:
    ctx = build_target_context(employee)
    if search_result.get("role") and not ctx["role"]:
        ctx["role"] = search_result["role"]
    if search_result.get("linkedin_url") and not ctx["linkedin_url"]:
        ctx["linkedin_url"] = search_result["linkedin_url"]
    if search_result.get("recent_news"):
        ctx["recent_news"] = search_result["recent_news"]
    return ctx


# ── Simple in-memory cache ────────────────────────────────────────

_cache: dict[tuple[str, str], dict[str, Any]] = {}


def _get_cached(key: tuple[str, str]) -> dict[str, Any] | None:
    return _cache.get(key)


def _set_cache(key: tuple[str, str], value: dict[str, Any]) -> None:
    if len(_cache) > 512:
        _cache.clear()
    _cache[key] = value


def clear_cache() -> None:
    _cache.clear()
