"""Guard: secrets from .env must never reach tracked files.

All credentials live in .env, which is gitignored. This test keeps it that
way two ways: .env itself stays untracked (and un-ignoreable), and no live
secret value may appear in any tracked file — so a future debug paste,
hardcoded fallback, or copied config fails CI before it can be pushed and
flagged by secret scanners.
"""
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".env"

# Keys whose values are credentials or crypto material. Other .env values
# (hosts, model names, regions) are not secrets and may legitimately appear
# in docs/code.
_SECRET_KEY_MARKERS = ("KEY", "SECRET", "TOKEN", "PASSWORD", "PASS", "SALT", "SID")


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True
    )


def test_env_is_gitignored():
    proc = _git("check-ignore", ".env")
    assert proc.returncode == 0 and proc.stdout.strip() == ".env", (
        ".env must be covered by .gitignore so it cannot be added accidentally"
    )


def test_env_is_not_tracked():
    proc = _git("ls-files")
    assert ".env" not in proc.stdout.splitlines(), (
        ".env is tracked by git — remove it from the index (git rm --cached .env) "
        "and rotate every credential inside it"
    )


def _env_secret_values() -> list[tuple[str, str]]:
    if not ENV_FILE.exists():
        return []
    pairs = []
    for line in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip("'\"")
        if (
            any(marker in key.upper() for marker in _SECRET_KEY_MARKERS)
            and len(value) >= 8
        ):
            pairs.append((key, value))
    return pairs


@pytest.mark.parametrize(
    "key_value", _env_secret_values(), ids=lambda kv: kv[0]
)
def test_secret_value_absent_from_tracked_files(key_value: tuple[str, str]):
    key, value = key_value
    proc = _git("grep", "-q", "-F", "-e", value, "--", ".")
    assert proc.returncode != 0, (
        f"Value of {key} from .env appears in tracked files — remove it, purge it "
        "from history if it was ever committed, and rotate the credential"
    )
