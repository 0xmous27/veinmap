"""Credential model — CRUD and suggestion engine."""
from veinmap.db import get_db


def add_credential(username: str, secret: str, cred_type: str, domain: str = None,
                   source_ip: str = None, source_method: str = None, notes: str = None) -> int:
    conn = get_db()
    source_host_id = None
    if source_ip:
        host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (source_ip,)).fetchone()
        if host:
            source_host_id = host["id"]
    cur = conn.execute(
        "INSERT INTO credentials (username, secret, cred_type, domain, source_host_id, source_method, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (username, secret, cred_type, domain, source_host_id, source_method, notes)
    )
    cred_id = cur.lastrowid
    conn.execute(
        "INSERT INTO timeline (category, description, credential_id) VALUES ('loot', ?, ?)",
        (f"Credential found: {domain + '/' if domain else ''}{username} ({cred_type})", cred_id)
    )
    conn.commit()
    conn.close()
    return cred_id


def list_credentials(cred_type: str = None, source_ip: str = None) -> list:
    conn = get_db()
    query = """SELECT c.*, h.ip as source_ip FROM credentials c
               LEFT JOIN hosts h ON c.source_host_id = h.id WHERE 1=1"""
    params = []
    if cred_type:
        query += " AND c.cred_type = ?"
        params.append(cred_type)
    if source_ip:
        query += " AND h.ip = ?"
        params.append(source_ip)
    query += " ORDER BY c.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def mark_tested(cred_id: int, host_ip: str, status: str, service: str = None):
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (host_ip,)).fetchone()
    if not host:
        conn.close()
        return False
    conn.execute(
        """INSERT INTO cred_host_map (credential_id, host_id, status, service, tested_at)
           VALUES (?, ?, ?, ?, datetime('now'))
           ON CONFLICT(id) DO UPDATE SET status=?, tested_at=datetime('now')""",
        (cred_id, host["id"], status, service, status)
    )
    conn.commit()
    conn.close()
    return True


def suggest_untested() -> list:
    """Find credential/host combinations not yet tested."""
    conn = get_db()
    rows = conn.execute("""
        SELECT c.id as cred_id, c.username, c.secret, c.cred_type, c.domain, h.ip, h.hostname
        FROM credentials c
        CROSS JOIN hosts h
        WHERE h.status != 'owned'
        AND NOT EXISTS (
            SELECT 1 FROM cred_host_map m
            WHERE m.credential_id = c.id AND m.host_id = h.id
        )
        ORDER BY c.created_at DESC
        LIMIT 20
    """).fetchall()
    conn.close()
    return rows


def delete_credential(cred_id: int) -> bool:
    conn = get_db()
    cur = conn.execute("DELETE FROM credentials WHERE id = ?", (cred_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0
