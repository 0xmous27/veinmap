"""Database layer — SQLite with WAL mode for crash safety."""
import sqlite3
from pathlib import Path

DEFAULT_DB = Path.home() / ".veinmap" / "default.db"


def _get_active_db_path() -> Path:
    """Get the active engagement database path."""
    marker = Path.home() / ".veinmap" / ".active"
    if marker.exists():
        name = marker.read_text().strip()
        return Path.home() / ".veinmap" / f"{name}.db"
    return DEFAULT_DB

SCHEMA = """
CREATE TABLE IF NOT EXISTS engagement (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT,
    start_date TEXT NOT NULL DEFAULT (date('now')),
    end_date TEXT,
    scope_description TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS hosts (
    id INTEGER PRIMARY KEY,
    ip TEXT NOT NULL UNIQUE,
    hostname TEXT,
    os TEXT,
    network_segment TEXT,
    status TEXT DEFAULT 'discovered' CHECK(status IN ('discovered','enumerated','foothold','privesc','owned')),
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    port INTEGER NOT NULL,
    protocol TEXT DEFAULT 'tcp',
    service_name TEXT,
    version TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS credentials (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    secret TEXT NOT NULL,
    cred_type TEXT NOT NULL CHECK(cred_type IN ('password','ntlm','kerberos','ssh_key','other')),
    domain TEXT,
    source_host_id INTEGER REFERENCES hosts(id),
    source_method TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cred_host_map (
    id INTEGER PRIMARY KEY,
    credential_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'untested' CHECK(status IN ('valid','invalid','untested')),
    service TEXT,
    tested_at TEXT
);

CREATE TABLE IF NOT EXISTS checklist_state (
    id INTEGER PRIMARY KEY,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    checklist_file TEXT NOT NULL,
    item_id TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    notes TEXT,
    UNIQUE(host_id, checklist_file, item_id)
);

CREATE TABLE IF NOT EXISTS pivots (
    id INTEGER PRIMARY KEY,
    source_host_id INTEGER NOT NULL REFERENCES hosts(id),
    destination_subnet TEXT NOT NULL,
    method TEXT NOT NULL,
    local_port INTEGER,
    command TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active','closed')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS timeline (
    id INTEGER PRIMARY KEY,
    timestamp TEXT DEFAULT (datetime('now')),
    host_id INTEGER REFERENCES hosts(id),
    category TEXT CHECK(category IN ('recon','enumeration','exploitation','privesc','lateral','persistence','loot','other')),
    description TEXT NOT NULL,
    evidence TEXT,
    credential_id INTEGER REFERENCES credentials(id),
    finding_id INTEGER REFERENCES findings(id)
);

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('critical','high','medium','low','info')),
    description TEXT,
    impact TEXT,
    steps_to_reproduce TEXT,
    remediation TEXT,
    cvss_score REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS finding_hosts (
    finding_id INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    PRIMARY KEY (finding_id, host_id)
);

CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY,
    finding_id INTEGER REFERENCES findings(id) ON DELETE CASCADE,
    timeline_id INTEGER REFERENCES timeline(id),
    evidence_type TEXT CHECK(evidence_type IN ('text','screenshot','file')),
    content TEXT NOT NULL,
    caption TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


def get_db(db_path: Path = None) -> sqlite3.Connection:
    """Get database connection with WAL mode enabled."""
    path = db_path or _get_active_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = None) -> sqlite3.Connection:
    """Initialize database with schema."""
    conn = get_db(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
