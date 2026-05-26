"""Report generation engine — Jinja2 templates to Markdown."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from veinmap.db import get_db

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"


def generate_report(template_name: str = "report_cpts.md.j2", output_path: str = None) -> str:
    """Generate a pentest report from engagement data."""
    conn = get_db()

    hosts = conn.execute("SELECT * FROM hosts ORDER BY ip").fetchall()
    findings = conn.execute(
        """SELECT * FROM findings ORDER BY
           CASE severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1
           WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END"""
    ).fetchall()
    timeline = conn.execute(
        "SELECT t.*, h.ip as host_ip FROM timeline t LEFT JOIN hosts h ON t.host_id = h.id ORDER BY t.timestamp"
    ).fetchall()
    credentials = conn.execute(
        "SELECT c.*, h.ip as source_ip FROM credentials c LEFT JOIN hosts h ON c.source_host_id = h.id"
    ).fetchall()
    pivots = conn.execute(
        "SELECT p.*, h.ip as source_ip FROM pivots p JOIN hosts h ON p.source_host_id = h.id"
    ).fetchall()

    # Enrich findings with hosts and evidence
    enriched_findings = []
    for f in findings:
        f_hosts = conn.execute(
            "SELECT h.ip, h.hostname FROM hosts h JOIN finding_hosts fh ON h.id = fh.host_id WHERE fh.finding_id = ?",
            (f["id"],)
        ).fetchall()
        evidence = conn.execute("SELECT * FROM evidence WHERE finding_id = ?", (f["id"],)).fetchall()
        enriched_findings.append({
            **dict(f),
            "hosts": [h["ip"] + (f" ({h['hostname']})" if h["hostname"] else "") for h in f_hosts],
            "evidence": [dict(e) for e in evidence],
        })

    conn.close()

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_name)

    report = template.render(
        hosts=[dict(h) for h in hosts],
        findings=enriched_findings,
        timeline=[dict(t) for t in timeline],
        credentials=[dict(c) for c in credentials],
        pivots=[dict(p) for p in pivots],
        total_hosts=len(hosts),
        owned_hosts=len([h for h in hosts if h["status"] == "owned"]),
    )

    if output_path:
        Path(output_path).write_text(report)
    return report
