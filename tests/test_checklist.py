"""Tests for checklist engine."""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    with patch("veinmap.db._get_active_db_path", return_value=db_path):
        from veinmap.db import init_db
        init_db(db_path)
        yield db_path
    db_path.unlink(missing_ok=True)


def test_load_checklist():
    from veinmap.engines.checklist_engine import load_checklist
    cl = load_checklist("smb")
    assert cl is not None
    assert cl["service"] == "smb"
    assert 445 in cl["ports"]
    assert "enumeration" in cl["categories"]


def test_available_checklists():
    from veinmap.engines.checklist_engine import get_available_checklists
    available = get_available_checklists()
    assert "smb" in available
    assert "http" in available
    assert "kerberos" in available
    assert len(available) >= 13


def test_check_uncheck(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host
        from veinmap.engines.checklist_engine import check_item, get_checklist_state
        add_host("10.10.14.5")
        check_item("10.10.14.5", "smb", "smb_null_session")
        state = get_checklist_state("10.10.14.5", "smb")
        assert state["progress"]["done"] == 1
        assert state["progress"]["percent"] > 0
