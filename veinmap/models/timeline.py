"""Timeline model — chronological attack log."""
from veinmap.db import get_db


def add_entry(description: str, host_ip: str = None, category: str = "other", evidence: str = None) -> int:
    conn = get_db()
    host_id = None
    if host_ip:
        host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (host_ip,)).fetchone()
        if host:
            host_id = host["id"]
    cur = conn.execute(
        "INSERT INTO timeline (host_id, category, description, evidence) VALUES (?, ?, ?, ?)",
        (host_id, category, description, evidence)
    )
    conn.commit()
    entry_id = cur.lastrowid
    conn.close()
    return entry_id


def list_entries(host_ip: str = None, category: str = None, limit: int = 50) -> list:
    conn = get_db()
    query = """SELECT t.*, h.ip as host_ip, h.hostname
               FROM timeline t LEFT JOIN hosts h ON t.host_id = h.id WHERE 1=1"""
    params = []
    if host_ip:
        query += " AND h.ip = ?"
        params.append(host_ip)
    if category:
        query += " AND t.category = ?"
        params.append(category)
    query += " ORDER BY t.timestamp DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows
