"""Tests for credential management."""
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


def test_add_credential(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.credential import add_credential, list_credentials
        cred_id = add_credential("admin", "Password123", "password", "corp.local")
        assert cred_id == 1
        creds = list_credentials()
        assert len(creds) == 1
        assert creds[0]["username"] == "admin"


def test_suggest_untested(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host
        from veinmap.models.credential import add_credential, suggest_untested
        add_host("10.10.14.5")
        add_credential("admin", "pass", "password")
        suggestions = suggest_untested()
        assert len(suggestions) == 1
        assert suggestions[0]["ip"] == "10.10.14.5"


def test_mark_tested(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host
        from veinmap.models.credential import add_credential, mark_tested, suggest_untested
        add_host("10.10.14.5")
        cred_id = add_credential("admin", "pass", "password")
        mark_tested(cred_id, "10.10.14.5", "valid")
        suggestions = suggest_untested()
        assert len(suggestions) == 0
