"""Tests for host management."""
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    with patch("veinmap.db._get_active_db_path", return_value=db_path):
        from veinmap.db import init_db
        init_db(db_path)
        yield db_path
    db_path.unlink(missing_ok=True)


def test_add_host(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host, get_host
        host_id = add_host("10.10.14.5", "DC01", "Windows Server 2019", "internal")
        assert host_id == 1
        host = get_host("10.10.14.5")
        assert host["hostname"] == "DC01"
        assert host["os"] == "Windows Server 2019"
        assert host["status"] == "discovered"


def test_update_status(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host, update_status, get_host
        add_host("10.10.14.5")
        update_status("10.10.14.5", "owned")
        host = get_host("10.10.14.5")
        assert host["status"] == "owned"


def test_add_service(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host, add_service, get_services
        add_host("10.10.14.5")
        add_service("10.10.14.5", 445, "tcp", "smb")
        services = get_services("10.10.14.5")
        assert len(services) == 1
        assert services[0]["port"] == 445
        assert services[0]["service_name"] == "smb"


def test_delete_host(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host, delete_host, get_host
        add_host("10.10.14.5")
        assert delete_host("10.10.14.5") is True
        assert get_host("10.10.14.5") is None


def test_list_hosts_filter(test_db):
    with patch("veinmap.db._get_active_db_path", return_value=test_db):
        from veinmap.models.host import add_host, list_hosts, update_status
        add_host("10.10.14.5", segment="internal")
        add_host("10.10.14.8", segment="dmz")
        hosts = list_hosts(segment="internal")
        assert len(hosts) == 1
        assert hosts[0]["ip"] == "10.10.14.5"
