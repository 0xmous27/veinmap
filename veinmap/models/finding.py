"""Finding model — vulnerability documentation."""
from veinmap.db import get_db


def add_finding(title: str, severity: str, host_ips: list = None, description: str = None,
                impact: str = None, steps: str = None, remediation: str = None, cvss: float = None) -> int:
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO findings (title, severity, description, impact, steps_to_reproduce, remediation, cvss_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, severity, description, impact, steps, remediation, cvss)
    )
    finding_id = cur.lastrowid
    if host_ips:
        for ip in host_ips:
            host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (ip,)).fetchone()
            if host:
                conn.execute("INSERT OR IGNORE INTO finding_hosts (finding_id, host_id) VALUES (?, ?)",
                             (finding_id, host["id"]))
    conn.execute(
        "INSERT INTO timeline (category, description, finding_id) VALUES ('exploitation', ?, ?)",
        (f"Finding: [{severity.upper()}] {title}", finding_id)
    )
    conn.commit()
    conn.close()
    return finding_id


def list_findings(severity: str = None, host_ip: str = None) -> list:
    conn = get_db()
    query = """SELECT DISTINCT f.* FROM findings f"""
    params = []
    if host_ip:
        query += " JOIN finding_hosts fh ON f.id = fh.finding_id JOIN hosts h ON fh.host_id = h.id"
        query += " WHERE h.ip = ?"
        params.append(host_ip)
    elif severity:
        query += " WHERE f.severity = ?"
        params.append(severity)
    query += " ORDER BY CASE f.severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def add_evidence(finding_id: int, content: str, evidence_type: str = "text", caption: str = None) -> int:
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO evidence (finding_id, evidence_type, content, caption) VALUES (?, ?, ?, ?)",
        (finding_id, evidence_type, content, caption)
    )
    conn.commit()
    ev_id = cur.lastrowid
    conn.close()
    return ev_id


def get_finding(finding_id: int):
    conn = get_db()
    finding = conn.execute("SELECT * FROM findings WHERE id = ?", (finding_id,)).fetchone()
    if not finding:
        conn.close()
        return None, [], []
    hosts = conn.execute(
        "SELECT h.* FROM hosts h JOIN finding_hosts fh ON h.id = fh.host_id WHERE fh.finding_id = ?",
        (finding_id,)
    ).fetchall()
    evs = conn.execute("SELECT * FROM evidence WHERE finding_id = ?", (finding_id,)).fetchall()
    conn.close()
    return finding, hosts, evs
