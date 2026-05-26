"""Checklist engine — loads YAML checklists and tracks per-host state."""
from pathlib import Path
from datetime import datetime
import yaml
from veinmap.db import get_db

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "checklists"


def load_checklist(service: str) -> dict:
    """Load a checklist YAML file by service name."""
    path = DATA_DIR / f"{service}.yaml"
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def get_available_checklists() -> list:
    """List all available checklist files."""
    if not DATA_DIR.exists():
        return []
    return [f.stem for f in DATA_DIR.glob("*.yaml")]


def get_checklists_for_host(host_ip: str) -> list:
    """Get relevant checklists based on host's open ports."""
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (host_ip,)).fetchone()
    if not host:
        conn.close()
        return []
    services = conn.execute("SELECT port, service_name FROM services WHERE host_id = ?", (host["id"],)).fetchall()
    conn.close()

    matched = []
    for checklist_name in get_available_checklists():
        cl = load_checklist(checklist_name)
        if not cl:
            continue
        cl_ports = cl.get("ports", [])
        for svc in services:
            if svc["port"] in cl_ports or (svc["service_name"] and svc["service_name"].lower() == checklist_name):
                matched.append(checklist_name)
                break
    return matched


def get_checklist_state(host_ip: str, service: str) -> dict:
    """Get checklist with completion state for a host."""
    cl = load_checklist(service)
    if not cl:
        return None

    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (host_ip,)).fetchone()
    if not host:
        conn.close()
        return None

    completed = conn.execute(
        "SELECT item_id FROM checklist_state WHERE host_id = ? AND checklist_file = ? AND completed = 1",
        (host["id"], service)
    ).fetchall()
    conn.close()

    completed_ids = {r["item_id"] for r in completed}
    total = 0
    done = 0
    for category, items in cl.get("categories", {}).items():
        for item in items:
            total += 1
            item["completed"] = item["id"] in completed_ids
            if item["completed"]:
                done += 1

    cl["progress"] = {"total": total, "done": done, "percent": int((done / total * 100) if total else 0)}
    return cl


def check_item(host_ip: str, service: str, item_id: str) -> bool:
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (host_ip,)).fetchone()
    if not host:
        conn.close()
        return False
    conn.execute(
        """INSERT INTO checklist_state (host_id, checklist_file, item_id, completed, completed_at)
           VALUES (?, ?, ?, 1, ?)
           ON CONFLICT(host_id, checklist_file, item_id) DO UPDATE SET completed=1, completed_at=?""",
        (host["id"], service, item_id, datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return True


def uncheck_item(host_ip: str, service: str, item_id: str) -> bool:
    conn = get_db()
    host = conn.execute("SELECT id FROM hosts WHERE ip = ?", (host_ip,)).fetchone()
    if not host:
        conn.close()
        return False
    conn.execute(
        """INSERT INTO checklist_state (host_id, checklist_file, item_id, completed)
           VALUES (?, ?, ?, 0)
           ON CONFLICT(host_id, checklist_file, item_id) DO UPDATE SET completed=0, completed_at=NULL""",
        (host["id"], service, item_id)
    )
    conn.commit()
    conn.close()
    return True
