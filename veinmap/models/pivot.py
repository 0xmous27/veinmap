"""Pivot model — track network tunnels and reachability."""
from veinmap.db import get_db


def add_pivot(source_ip: str, dest_subnet: str, method: str, local_port: int = None, command: str = None) -> int:
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (source_ip,)).fetchone()
    if not host:
        conn.close()
        return None
    cur = conn.execute(
        "INSERT INTO pivots (source_host_id, destination_subnet, method, local_port, command) VALUES (?, ?, ?, ?, ?)",
        (host["id"], dest_subnet, method, local_port, command)
    )
    conn.execute(
        "INSERT INTO timeline (host_id, category, description) VALUES (?, 'lateral', ?)",
        (host["id"], f"Pivot established: {source_ip} → {dest_subnet} via {method}")
    )
    conn.commit()
    pivot_id = cur.lastrowid
    conn.close()
    return pivot_id


def list_pivots(active_only: bool = True) -> list:
    conn = get_db()
    query = """SELECT p.*, h.ip as source_ip, h.hostname as source_hostname
               FROM pivots p JOIN hosts h ON p.source_host_id = h.id"""
    if active_only:
        query += " WHERE p.status = 'active'"
    query += " ORDER BY p.created_at DESC"
    rows = conn.execute(query).fetchall()
    conn.close()
    return rows


def close_pivot(pivot_id: int) -> bool:
    conn = get_db()
    cur = conn.execute("UPDATE pivots SET status = 'closed' WHERE id = ?", (pivot_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0
