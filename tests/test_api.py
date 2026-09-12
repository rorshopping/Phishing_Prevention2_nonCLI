"""HTTP-layer smoke tests: boot the FastAPI app and exercise DB-free routes.

Covers the public web surface (homepage, legal pages, SEO files, console)
and the ops auth wiring. The static/ -> root byte mirror is enforced by
tests/test_root_mirror.py; DB-backed endpoints are out of scope here.
"""
import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app


@pytest.fixture
def client():
    # Deliberately no `with`: TestClient only runs lifespan events inside a
    # context manager, and startup would create tables in the real database
    # and start the background scheduler when GOPHISH_API_KEY is set.
    return TestClient(app)


@pytest.mark.parametrize(
    "path,marker",
    [
        ("/", "Phishing-Simulation und Security Awareness"),
        ("/privacy", "Datenschutzerklärung"),
        ("/impressum", "Impressum"),
        ("/data-processing-agreement", "Data Processing Agreement"),
        ("/console", "Operations Console"),
    ],
)
def test_serves_page_with_title(client, path, marker):
    resp = client.get(path)
    assert resp.status_code == 200, resp.text[:200]
    assert "text/html" in resp.headers["content-type"]
    assert marker in resp.text


def test_unknown_path_serves_custom_404(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert "Seite nicht gefunden" in resp.text


@pytest.mark.parametrize(
    "path,snippet",
    [
        ("/robots.txt", "Sitemap:"),
        ("/llms.txt", ""),
        ("/llms-full.txt", ""),
        ("/sitemap.xml", "<?xml"),
    ],
)
def test_seo_files_served(client, path, snippet):
    resp = client.get(path)
    assert resp.status_code == 200, resp.text[:200]
    assert len(resp.text.strip()) > 0
    if snippet:
        assert snippet in resp.text


def test_ops_config_reports_auth_state(client, monkeypatch):
    monkeypatch.setattr(settings, "ops_token", "")
    body = client.get("/ops/config").json()
    assert body["auth_required"] is False
    assert "version" in body


def test_ops_endpoints_reject_missing_or_wrong_token(client, monkeypatch):
    monkeypatch.setattr(settings, "ops_token", "secret-token")
    assert client.get("/ops/status").status_code == 401
    assert (
        client.get(
            "/ops/status", headers={"Authorization": "Bearer wrong-token"}
        ).status_code
        == 401
    )
    assert (
        client.get(
            "/ops/status", headers={"Authorization": "secret-token"}
        ).status_code
        == 401
    )
