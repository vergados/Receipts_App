"""Migrations must build a working database from nothing, and upgrade old ones."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect

from app.core.config import settings
from app.models.db.base import Base
import app.models.db  # noqa: F401  (registers every model on Base)

BACKEND_ROOT = Path(__file__).resolve().parents[3]


def _alembic_config() -> AlembicConfig:
    cfg = AlembicConfig(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    return cfg


@pytest.fixture
def database_url(tmp_path, monkeypatch) -> str:
    # env.py reads settings.database_url, so point it at a throwaway file
    url = f"sqlite:///{tmp_path / 'migrations.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    return url


def test_upgrade_from_empty_creates_every_model_table(database_url):
    command.upgrade(_alembic_config(), "head")

    tables = set(inspect(create_engine(database_url)).get_table_names())
    assert set(Base.metadata.tables) <= tables


def test_upgrade_database_made_by_create_all(database_url):
    # Older local databases were built with init_db.py (create_all) and
    # stamped at 0003; 0004 must not fail on the columns they already have.
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    command.stamp(_alembic_config(), "0003_add_organizations")

    command.upgrade(_alembic_config(), "head")

    with engine.connect() as conn:
        version = conn.exec_driver_sql("select version_num from alembic_version").scalar()
    assert version == "0004_newsroom_receipts"
