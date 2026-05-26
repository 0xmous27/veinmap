"""Host model — CRUD operations for target hosts."""
from datetime import datetime
from veinmap.db import get_db


def add_host(ip: str, hostname: str = None, os: str = None, segment: str = None, notes: str = None) -> int:
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO hosts (ip, hostname, os, network_segment, notes) VALUES (?, ?, ?, ?, ?)",
        (ip, hostname, os, segment, notes)
    )
    host_id = cur.lastrowid
    # Auto-log to timeline
    conn.execute(
        "INSERT INTO timeline (host_id, category, description) VALUES (?, 'recon', ?)",
        (host_id, f"Host discovered: {ip}" + (f" ({hostname})" if hostname else ""))
    )
    conn.commit()
    conn.close()
    return host_id


def list_hosts(segment: str = None, status: str = None) -> list:
    conn = get_db()
    query = "SELECT * FROM hosts WHERE 1=1"
    params = []
    if segment:
        query += " AND network_segment = ?"
        params.append(segment)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_host(ip: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM hosts WHERE ip = ?", (ip,)).fetchone()
    conn.close()
    return row


def get_host_by_id(host_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM hosts WHERE id = ?", (host_id,)).fetchone()
    conn.close()
    return row


VALID_STATUSES = ("discovered", "enumerated", "foothold", "privesc", "owned")


def update_status(ip: str, status: str) -> bool:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
    conn = get_db()
    conn.execute(
        "UPDATE hosts SET status = ?, updated_at = ? WHERE ip = ?",
        (status, datetime.now().isoformat(), ip)
    )
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (ip,)).fetchone()
    if host:
        conn.execute(
            "INSERT INTO timeline (host_id, category, description) VALUES (?, 'exploitation', ?)",
            (host["id"], f"Status changed to: {status}")
        )
    conn.commit()
    conn.close()
    return host is not None


def add_service(ip: str, port: int, protocol: str = "tcp", service_name: str = None, version: str = None):
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (ip,)).fetchone()
    if not host:
        conn.close()
        return None
    cur = conn.execute(
        "INSERT OR REPLACE INTO services (host_id, port, protocol, service_name, version) VALUES (?, ?, ?, ?, ?)",
        (host["id"], port, protocol, service_name, version)
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def get_services(ip: str) -> list:
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (ip,)).fetchone()
    if not host:
        conn.close()
        return []
    rows = conn.execute("SELECT * FROM services WHERE host_id = ? ORDER BY port", (host["id"],)).fetchall()
    conn.close()
    return rows


def delete_host(ip: str) -> bool:
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (ip,)).fetchone()
    if not host:
        conn.close()
        return False
    # Clear timeline references first (timeline doesn't cascade)
    conn.execute("UPDATE timeline SET host_id = NULL WHERE host_id = ?", (host["id"],))
    conn.execute("DELETE FROM hosts WHERE ip = ?", (ip,))
    conn.commit()
    conn.close()
    return True
