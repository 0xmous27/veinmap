"""Tests for CLI commands."""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from veinmap.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    with patch("veinmap.db._get_active_db_path", return_value=db_path):
        from veinmap.db import init_db
        init_db(db_path)
        yield db_path
    db_path.unlink(missing_ok=True)


def test_host_add(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        result = runner.invoke(app, ["host", "add", "10.10.14.5", "--hostname", "DC01"])
        assert result.exit_code == 0
        assert "Host added" in result.stdout


def test_host_list(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        runner.invoke(app, ["host", "add", "10.10.14.5"])
        result = runner.invoke(app, ["host", "list"])
        assert result.exit_code == 0
        assert "10.10.14.5" in result.stdout


def test_search(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        runner.invoke(app, ["host", "add", "10.10.14.5", "--hostname", "DC01"])
        result = runner.invoke(app, ["search", "DC01"])
        assert result.exit_code == 0
        assert "DC01" in result.stdout
