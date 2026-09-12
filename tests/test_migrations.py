"""Migration contract: `alembic upgrade head` builds the full model schema.

Runs Alembic programmatically against a throwaway SQLite file so schema
drift (models edited without a migration) fails in CI instead of in prod.
"""
import asyncio
import os

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from src.database.session import Base
import src.database.models  # noqa: F401  (registers all tables on Base.metadata)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def alembic_db_url(tmp_path):
    return f"sqlite+aiosqlite:///{tmp_path.as_posix()}/migrations.db"


@pytest.fixture
def alembic_config(alembic_db_url, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", alembic_db_url)
    monkeypatch.chdir(REPO_ROOT)
    return Config("alembic.ini")


async def _table_names(db_url: str) -> set[str]:
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        names = await conn.run_sync(lambda c: set(inspect(c).get_table_names()))
    await engine.dispose()
    return names


def test_upgrade_head_builds_full_model_schema(alembic_config, alembic_db_url):
    command.upgrade(alembic_config, "head")

    tables = asyncio.run(_table_names(alembic_db_url))
    expected = set(Base.metadata.tables)
    assert expected <= tables
    assert tables - expected == {"alembic_version"}


def test_downgrade_base_drops_all_model_tables(alembic_config, alembic_db_url):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")

    tables = asyncio.run(_table_names(alembic_db_url))
    assert not (set(Base.metadata.tables) & tables)


def test_upgrade_at_head_is_idempotent(alembic_config):
    command.upgrade(alembic_config, "head")
    # No-op when already at head; raises if revisions are inconsistent.
    command.upgrade(alembic_config, "head")
