"""Tests for AI-SEO / LLM visibility files (llms.txt, llms-full.txt, robots.txt).

Includes an "LLM prompt test": a small grader that simulates an LLM being
asked entity-clarity questions and verifies the plain-language content in
llms.txt / llms-full.txt is sufficient to answer them.
"""
from pathlib import Path

import pytest
from fastapi.responses import PlainTextResponse

from src.llms_txt import get_llms_txt, get_llms_full_txt, get_robots_txt

BASE_URL = "https://phishdefend-ai.vercel.app"


def _read(name: str) -> str:
    path = Path(__file__).resolve().parent.parent / name
    assert path.exists(), f"Missing file: {name}"
    return path.read_text(encoding="utf-8")


def test_main_wires_llms_routes():
    main_py = _read("src/main.py")
    assert "from src.llms_txt import" in main_py
    assert '@app.get("/llms.txt"' in main_py
    assert '@app.get("/llms-full.txt"' in main_py
    assert '@app.get("/robots.txt"' in main_py


def test_main_sitemap_route_reads_static_file():
    main_py = _read("src/main.py")
    assert '@app.get("/sitemap.xml"' in main_py
    assert '_read_static("sitemap.xml")' in main_py


def test_sitemap_discloses_llms_urls():
    sitemap = _read("static/sitemap.xml")
    assert f"{BASE_URL}/llms.txt" in sitemap
    assert f"{BASE_URL}/llms-full.txt" in sitemap
    assert "<urlset" in sitemap and "</urlset>" in sitemap


def test_root_mirrors_static_serving_files():
    for name in ("robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt"):
        assert _read(name) == _read(f"static/{name}")


def test_served_llms_matches_root():
    assert get_llms_txt() == _read("llms.txt")
    assert get_llms_full_txt() == _read("llms-full.txt")


def test_sitemap_llms_entries_valid_xml():
    import xml.etree.ElementTree as ET

    root_path = Path(__file__).resolve().parent.parent / "sitemap.xml"
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locs = [u.find(f"{ns}loc").text for u in ET.parse(root_path).getroot()]
    assert f"{BASE_URL}/llms.txt" in locs
    assert f"{BASE_URL}/llms-full.txt" in locs


# ---------- file presence & structure ----------


def test_llms_txt_exists_in_repo_root():
    content = _read("llms.txt")
    assert content.startswith("# PhishDefend AI")


def test_llms_txt_under_2kb():
    assert len(_read("llms.txt").encode("utf-8")) <= 2048


def test_llms_txt_reflects_site_state():
    content = _read("llms.txt")
    assert "1,000" in content and "2,500" in content
    assert "NIS2" in content and "ISO 27001" in content
    assert "smishing" in content.lower()


def test_llms_txt_reflects_new_sections():
    content = _read("llms.txt")
    assert "anti-phishing" in content.lower()
    assert "KMU" in content
    assert "KnowBe4" in content and "SoSafe" in content and "Hoxhunt" in content
    assert "no sanctions" in content and "security culture" in content


def test_llms_txt_reflects_trust_section():
    content = _read("llms.txt")
    assert "TLS 1.3" in content
    assert "90 days" in content and "7 days" in content
    assert "Frankfurt" in content


def test_llms_full_txt_exists_in_repo_root():
    content = _read("llms-full.txt")
    assert content.startswith("# PhishDefend AI")


def test_llms_full_txt_reflects_site_state():
    content = _read("llms-full.txt")
    assert "1,000" in content and "2,500" in content
    assert "NIS2" in content and "ISO 27001" in content and "A.6.3" in content
    assert "smishing" in content.lower()
    assert "11 questions" in content


def test_llms_full_txt_reflects_new_sections():
    content = _read("llms-full.txt")
    assert "Anti-Phishing-Training" in content
    assert "Mitarbeiter-Sicherheit" in content
    assert "KMU" in content
    assert "KnowBe4" in content and "SoSafe" in content and "Hoxhunt" in content
    assert "Benchmarks" in content and "140,000" in content


def test_llms_full_txt_reflects_trust_section():
    content = _read("llms-full.txt")
    assert "Trust & Security" in content
    assert "TLS 1.3" in content and "Frankfurt" in content
    assert "90 days" in content and "7 days" in content
    assert "A.6.3" in content and "A.5.36" in content


def test_index_contains_new_sections():
    index = _read("static/index.html")
    for tag in [
        "Anti-Phishing-Training",
        "Für KMU",
        "Vergleich &amp; Alternativen",
        "Mitarbeiter-Sicherheit",
        "Benchmarks &amp; ROI",
        "Vertrauen &amp; Sicherheit",
    ]:
        assert tag in index, f"missing section tag: {tag}"
    assert "KnowBe4" in index and "SoSafe" in index and "Hoxhunt" in index
    assert "trust-badge" in index
    assert "DPA / AVV nach Art. 28 DSGVO" in index


def test_index_faq_count_matches_site():
    index = _read("static/index.html")
    assert index.count('itemprop="mainEntity"') == 11
    assert '"@type": "Question"' in index


def test_llms_txt_links_to_llms_full():
    content = _read("llms.txt")
    assert "llms-full.txt" in content


_PLACEHOLDER_RE = r"YOUR_COMPANY_NAME_HERE|\[your@[^\]]*\]|\[dpo@[^\]]*\]|\[Street[^\]]*\]|\[Postal[^\]]*\]|\[Name[^\]]*\]|\[DE[^\]]*\]|\[[^\]]*(XXX|xxxxx|placeholder|company|email)[^\]]*\]|lorem|TODO|FIXME|REPLACE_WITH"


@pytest.mark.parametrize("name", ["llms.txt", "llms-full.txt"])
def test_llms_files_placeholder_free(name):
    import re

    content = _read(name)
    matches = re.findall(_PLACEHOLDER_RE, content, re.IGNORECASE)
    assert not matches, f"placeholder tokens found in {name}: {matches}"


@pytest.mark.parametrize("name", ["llms.txt", "llms-full.txt"])
def test_llms_files_no_h3_or_deeper_headings(name):
    import re

    content = _read(name)
    deep = [ln for ln in content.splitlines() if re.match(r"^#{3,}\s", ln)]
    assert not deep, f"H3+ headings found in {name}: {deep}"


def test_llms_links_resolve_to_existing_static_files():
    import re
    from urllib.parse import urlparse

    base = BASE_URL + "/"
    for name in ("llms.txt", "llms-full.txt"):
        content = _read(name)
        for url in re.findall(r"\]\((https?://[^)\s]+)\)", content):
            assert url.startswith(base), f"{name} links outside canonical domain: {url}"
            path = url[len(base):]
            candidates = [
                path or "index.html",
                f"{path}.html",
                path,
            ]
            if path.startswith("fonts/"):
                candidates.append(f"static/{path}")
            resolved = any(
                p and Path(__file__).resolve().parent.parent.joinpath(p).exists()
                for p in candidates
            )
            assert resolved, f"{name} link target does not exist in repo: {url}"


def test_robots_txt_has_ai_crawler_directives():
    content = _read("static/robots.txt")
    for agent in [
        "GPTBot",
        "OAI-SearchBot",
        "ClaudeBot",
        "anthropic-ai",
        "PerplexityBot",
        "Google-Extended",
    ]:
        assert f"User-agent: {agent}" in content, f"missing AI crawler: {agent}"
    assert "Sitemap: https://phishdefend-ai.vercel.app/sitemap.xml" in content


# ---------- serving ----------


def _response_body(response: PlainTextResponse) -> str:
    assert response.status_code == 200
    assert response.media_type == "text/plain"
    return response.body.decode("utf-8")


def test_robots_txt_served_with_ai_crawlers():
    body = get_robots_txt()
    assert "User-agent: GPTBot" in body
    assert "User-agent: ClaudeBot" in body
    assert "User-agent: PerplexityBot" in body


def test_robots_txt_endpoint_response_correct():
    body = _response_body(PlainTextResponse(get_robots_txt()))
    assert "User-agent: GPTBot" in body
    assert "Sitemap: https://phishdefend-ai.vercel.app/sitemap.xml" in body


def test_llms_txt_served_content():
    body = get_llms_txt()
    assert body.startswith("# PhishDefend AI")
    assert "What it does" in body
    assert "Who it is for" in body
    assert "What it offers" in body


def test_llms_txt_endpoint_response_correct():
    body = _response_body(PlainTextResponse(get_llms_txt()))
    assert body.startswith("# PhishDefend AI")
    assert "llms-full.txt" in body
    assert f"{BASE_URL}/llms-full.txt" in body


def test_llms_full_txt_served_content():
    body = get_llms_full_txt()
    assert "Entity Identity" in body
    assert "Pricing" in body


def test_llms_full_txt_endpoint_response_correct():
    body = _response_body(PlainTextResponse(get_llms_full_txt()))
    assert body.startswith("# PhishDefend AI")
    assert "Entity Identity" in body
    assert "Pricing" in body


# ---------- LLM prompt test ----------
# Simulates an LLM being prompted about the product. Each question maps to a
# list of answer fragments that must be present in the machine-readable text.


_LLM_QUESTIONS = {
    "What does PhishDefend AI do?": [
        "phishing simulation",
        "security awareness training",
        "automated",
    ],
    "Who is PhishDefend AI for?": [
        "SMEs",
        "KMU",
        "employees",
    ],
    "What does PhishDefend AI offer?": [
        "25",
        "campaigns",
        "vishing",
        "smishing",
        "reports",
    ],
    "How much does it cost?": [
        "1,000",
        "2,500",
    ],
    "Is it GDPR compliant?": [
        "GDPR",
        "Hetzner",
    ],
    "Does it support NIS2 and ISO 27001?": [
        "NIS2",
        "ISO 27001",
    ],
    "What security standards and trust measures does it meet?": [
        "TLS",
        "90 days",
        "A.6.3",
    ],
    "How does anti-phishing training work?": [
        "2-minute",
        "micro-training",
    ],
    "How does the platform treat employee mistakes (Mitarbeiter-Sicherheit)?": [
        "sanction",
        "culture",
    ],
    "How does PhishDefend AI compare to KnowBe4, SoSafe, Hoxhunt or gophish?": [
        "KnowBe4",
        "SoSafe",
        "Hoxhunt",
    ],
    "What is it also known as?": [
        "Phish Defend",
    ],
}


def _answer_fragments_present(content: str, fragments: list[str]) -> list[str]:
    return [f for f in fragments if f.lower() not in content.lower()]


@pytest.mark.parametrize("question", list(_LLM_QUESTIONS.keys()))
def test_llm_prompt_answered_by_llms_txt(question):
    content = _read("llms.txt")
    missing = _answer_fragments_present(content, _LLM_QUESTIONS[question])
    assert not missing, (
        f"LLM prompt '{question}' cannot be answered from llms.txt; "
        f"missing fragments: {missing}"
    )


@pytest.mark.parametrize("question", list(_LLM_QUESTIONS.keys()))
def test_llm_prompt_answered_by_llms_full_txt(question):
    content = _read("llms-full.txt")
    missing = _answer_fragments_present(content, _LLM_QUESTIONS[question])
    assert not missing, (
        f"LLM prompt '{question}' cannot be answered from llms-full.txt; "
        f"missing fragments: {missing}"
    )
