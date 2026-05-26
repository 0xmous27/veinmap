"""Tests for report generation."""
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


def test_generate_report(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host
        from veinmap.models.finding import add_finding
        from veinmap.engines.report_engine import generate_report
        add_host("10.10.14.5", "DC01", "Windows")
        add_finding("Test Finding", "critical", ["10.10.14.5"], "Description", remediation="Fix it")
        report = generate_report()
        assert "Penetration Test Report" in report
        assert "1 critical" in report
        assert "10.10.14.5" in report
        assert "Test Finding" in report
        assert "Fix it" in report


def test_generate_report_generic_template(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host
        from veinmap.engines.report_engine import generate_report
        add_host("10.10.14.5")
        report = generate_report(template_name="report_generic.md.j2")
        assert "10.10.14.5" in report
