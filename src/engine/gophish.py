import logging
from typing import Any

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class GophishClientError(Exception):
    pass


class GophishClient:
    def __init__(self) -> None:
        self.base_url = settings.gophish_api_url.rstrip("/")
        self.api_key = settings.gophish_api_key
        self._client: httpx.AsyncClient | None = None

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        client = self._client or httpx.AsyncClient(timeout=30.0, verify=False, follow_redirects=True)
        try:
            resp = await client.request(method, url, json=json, params=params, headers=headers)
            resp.raise_for_status()
            if resp.status_code == 204:
                return None
            return resp.json()
        except httpx.HTTPStatusError as e:
            detail = ""
            try:
                detail = e.response.json().get("message", e.response.text)
            except Exception:
                detail = e.response.text
            logger.error("Gophish API error %s %s: %s", method, path, detail)
            raise GophishClientError(f"Gophish API error ({e.response.status_code}): {detail}") from e
        except httpx.RequestError as e:
            logger.error("Gophish request failed %s %s: %s", method, path, e)
            raise GophishClientError(f"Gophish request failed: {e}") from e

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── Groups ──────────────────────────────────────────────────────

    async def create_group(self, name: str, targets: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {"name": name, "targets": targets}
        return await self._request("POST", "/groups/", json=payload)

    async def get_group(self, group_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/groups/{group_id}")

    # ── Templates ───────────────────────────────────────────────────

    async def create_template(
        self, name: str, subject: str, html: str, text: str = "", envelope_sender: str = ""
    ) -> dict[str, Any]:
        payload = {"name": name, "subject": subject, "html": html}
        if text:
            payload["text"] = text
        if envelope_sender:
            payload["envelope_sender"] = envelope_sender
        return await self._request("POST", "/templates/", json=payload)

    async def get_template(self, template_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/templates/{template_id}")

    # ── Landing Pages (Sending Profiles) ────────────────────────────

    async def create_page(
        self, name: str, html: str, capture_credentials: bool = True, capture_passwords: bool = True
    ) -> dict[str, Any]:
        payload = {
            "name": name,
            "html": html,
            "capture_credentials": capture_credentials,
            "capture_passwords": capture_passwords,
        }
        return await self._request("POST", "/pages/", json=payload)

    async def get_page(self, page_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/pages/{page_id}")

    # ── SMTP Profiles ───────────────────────────────────────────────

    async def create_smtp_profile(self, name: str, smtp: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "name": name,
            "interface_type": "SMTP",
            "from_address": smtp.get("from_address", settings.email_source),
            "host": smtp["host"],
            "username": smtp.get("username", ""),
            "password": smtp.get("password", ""),
            "port": smtp.get("port", 587),
            "ignore_cert_errors": smtp.get("ignore_cert_errors", True),
        }
        return await self._request("POST", "/smtp/", json=payload)

    # ── Campaigns ───────────────────────────────────────────────────

    async def create_campaign(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/campaigns/", json=payload)

    async def get_campaign(self, campaign_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/campaigns/{campaign_id}")

    async def complete_campaign(self, campaign_id: int) -> dict[str, Any]:
        return await self._request("PUT", f"/campaigns/{campaign_id}/complete")

    async def get_campaign_results(self, campaign_id: int) -> list[dict[str, Any]]:
        data = await self._request("GET", f"/campaigns/{campaign_id}")
        return data.get("results", [])
