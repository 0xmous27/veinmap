"""VeinMap CLI — main entry point."""
import typer
from typing import Optional, List
from rich.console import Console

from veinmap.db import init_db
from veinmap import tui

app = typer.Typer(help="VeinMap — Penetration Testing Engagement Tracker", no_args_is_help=True)
console = Console()

# --- Sub-commands ---
host_app = typer.Typer(help="Host management")
cred_app = typer.Typer(help="Credential management")
pivot_app = typer.Typer(help="Pivot/tunnel tracking")
timeline_app = typer.Typer(help="Attack timeline")
finding_app = typer.Typer(help="Finding management")
checklist_app = typer.Typer(help="Methodology checklists")
report_app = typer.Typer(help="Report generation")
cmd_app = typer.Typer(help="Command reference")

app.add_typer(host_app, name="host")
app.add_typer(cred_app, name="cred")
app.add_typer(pivot_app, name="pivot")
app.add_typer(timeline_app, name="timeline")
app.add_typer(finding_app, name="finding")
app.add_typer(checklist_app, name="checklist")
app.add_typer(report_app, name="report")
app.add_typer(cmd_app, name="cmd")


@app.command()
def init(name: str = typer.Argument("default", help="Engagement name")):
    """Initialize VeinMap database for an engagement."""
    from pathlib import Path
    db_path = Path.home() / ".veinmap" / f"{name}.db"
    init_db(db_path)
    # Write active engagement marker
    marker = Path.home() / ".veinmap" / ".active"
    marker.write_text(name)
    tui.banner()
    console.print(f"[green]✓ Engagement '{name}' initialized at {db_path}[/]")
    console.print("[yellow]⚠ Credentials are stored in plaintext. Do not use on shared systems.[/]")


@app.command()
def use(name: str = typer.Argument(..., help="Engagement name to switch to")):
    """Switch active engagement."""
    from pathlib import Path
    db_path = Path.home() / ".veinmap" / f"{name}.db"
    if not db_path.exists():
        console.print(f"[red]✗ Engagement '{name}' not found. Run: veinmap init {name}[/]")
        return
    marker = Path.home() / ".veinmap" / ".active"
    marker.write_text(name)
    console.print(f"[green]✓ Switched to engagement: {name}[/]")


@app.command("engagements")
def list_engagements():
    """List all engagements."""
    from pathlib import Path
    veinmap_dir = Path.home() / ".veinmap"
    if not veinmap_dir.exists():
        console.print("[yellow]No engagements found. Run: veinmap init[/]")
        return
    active = ""
    marker = veinmap_dir / ".active"
    if marker.exists():
        active = marker.read_text().strip()
    for db_file in sorted(veinmap_dir.glob("*.db")):
        name = db_file.stem
        indicator = " [green]← active[/]" if name == active else ""
        console.print(f"  • {name}{indicator}")


@app.command("export")
def export_db(output: str = typer.Argument(..., help="Output path for database copy")):
    """Export current engagement database."""
    import shutil
    from veinmap.db import _get_active_db_path
    src = _get_active_db_path()
    shutil.copy2(str(src), output)
    console.print(f"[green]✓ Exported to: {output}[/]")


@app.command("import")
def import_db(
    path: str = typer.Argument(..., help="Path to .db file to import"),
    name: str = typer.Option(None, "--name", "-n", help="Engagement name (default: filename)"),
):
    """Import an engagement database."""
    import shutil
    from pathlib import Path
    src = Path(path)
    if not src.exists():
        console.print(f"[red]✗ File not found: {path}[/]")
        return
    eng_name = name or src.stem
    dest = Path.home() / ".veinmap" / f"{eng_name}.db"
    shutil.copy2(str(src), str(dest))
    console.print(f"[green]✓ Imported as engagement: {eng_name}[/]")


# ═══════════════════════════════════════════
# HOST COMMANDS
# ═══════════════════════════════════════════

@host_app.command("add")
def host_add(
    ip: str = typer.Argument(..., help="Target IP address"),
    hostname: Optional[str] = typer.Option(None, "--hostname", "-n"),
    os: Optional[str] = typer.Option(None, "--os", "-o"),
    segment: Optional[str] = typer.Option(None, "--segment", "-s"),
):
    """Add a new target host."""
    from veinmap.models.host import add_host
    try:
        host_id = add_host(ip, hostname, os, segment)
        console.print(f"[green]✓ Host added:[/] {ip} (id={host_id})")
    except Exception as e:
        console.print(f"[red]✗ Error:[/] {e}")


@host_app.command("list")
def host_list(
    segment: Optional[str] = typer.Option(None, "--segment", "-s"),
    status: Optional[str] = typer.Option(None, "--status"),
):
    """List all hosts."""
    from veinmap.models.host import list_hosts
    hosts = list_hosts(segment, status)
    if not hosts:
        console.print("[yellow]No hosts found.[/]")
        return
    tui.print_hosts(hosts)


@host_app.command("status")
def host_status(
    ip: str = typer.Argument(..., help="Host IP"),
    new_status: str = typer.Argument(..., help="discovered|enumerated|foothold|privesc|owned"),
):
    """Update host compromise status."""
    from veinmap.models.host import update_status
    try:
        if update_status(ip, new_status):
            console.print(f"[green]✓ {ip} → {new_status}[/]")
        else:
            console.print(f"[red]✗ Host not found: {ip}[/]")
    except ValueError as e:
        console.print(f"[red]✗ {e}[/]")


@host_app.command("ports")
def host_ports(
    ip: str = typer.Argument(..., help="Host IP"),
    ports: List[str] = typer.Argument(..., help="port:service pairs (e.g., 445:smb 80:http)"),
):
    """Add ports/services to a host."""
    from veinmap.models.host import add_service
    for entry in ports:
        parts = entry.split(":")
        try:
            port = int(parts[0])
        except ValueError:
            console.print(f"[red]✗ Invalid port: '{parts[0]}' — must be a number[/]")
            continue
        svc = parts[1] if len(parts) > 1 else None
        add_service(ip, port, service_name=svc)
        console.print(f"[green]✓[/] {ip}:{port} ({svc or 'unknown'})")


@host_app.command("info")
def host_info(ip: str = typer.Argument(..., help="Host IP")):
    """Show detailed host info."""
    from veinmap.models.host import get_host, get_services
    host = get_host(ip)
    if not host:
        console.print(f"[red]✗ Host not found: {ip}[/]")
        return
    from rich.panel import Panel
    info = f"""[cyan]IP:[/] {host['ip']}
[cyan]Hostname:[/] {host['hostname'] or '-'}
[cyan]OS:[/] {host['os'] or '-'}
[cyan]Segment:[/] {host['network_segment'] or '-'}
[cyan]Status:[/] {host['status']}
[cyan]Added:[/] {host['created_at']}"""
    console.print(Panel(info, title=f"[bold]{ip}[/]", border_style="green"))
    services = get_services(ip)
    if services:
        from rich.table import Table
        t = Table(border_style="green")
        t.add_column("Port")
        t.add_column("Proto")
        t.add_column("Service")
        t.add_column("Version")
        for s in services:
            t.add_row(str(s["port"]), s["protocol"], s["service_name"] or "-", s["version"] or "-")
        console.print(t)


@host_app.command("rm")
def host_rm(ip: str = typer.Argument(..., help="Host IP to remove")):
    """Delete a host."""
    from veinmap.models.host import delete_host
    if delete_host(ip):
        console.print(f"[green]✓ Deleted: {ip}[/]")
    else:
        console.print(f"[red]✗ Host not found: {ip}[/]")


@host_app.command("edit")
def host_edit(
    ip: str = typer.Argument(..., help="Host IP to edit"),
    hostname: Optional[str] = typer.Option(None, "--hostname", "-n"),
    os: Optional[str] = typer.Option(None, "--os", "-o"),
    segment: Optional[str] = typer.Option(None, "--segment", "-s"),
    notes: Optional[str] = typer.Option(None, "--notes"),
):
    """Edit an existing host."""
    from veinmap.db import get_db
    from datetime import datetime
    conn = get_db()
    host = conn.execute("SELECT * FROM hosts WHERE ip = ?", (ip,)).fetchone()
    if not host:
        console.print(f"[red]✗ Host not found: {ip}[/]")
        conn.close()
        return
    updates = []
    params = []
    if hostname is not None:
        updates.append("hostname = ?")
        params.append(hostname)
    if os is not None:
        updates.append("os = ?")
        params.append(os)
    if segment is not None:
        updates.append("network_segment = ?")
        params.append(segment)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
    if not updates:
        console.print("[yellow]No changes specified.[/]")
        conn.close()
        return
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(ip)
    conn.execute(f"UPDATE hosts SET {', '.join(updates)} WHERE ip = ?", params)
    conn.commit()
    conn.close()
    console.print(f"[green]✓ Updated: {ip}[/]")


# ═══════════════════════════════════════════
# CREDENTIAL COMMANDS
# ═══════════════════════════════════════════

@cred_app.command("add")
def cred_add(
    username: str = typer.Argument(...),
    secret: str = typer.Argument(...),
    cred_type: str = typer.Option("password", "--type", "-t", help="password|ntlm|kerberos|ssh_key|other"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d"),
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Source host IP"),
    method: Optional[str] = typer.Option(None, "--method", "-m", help="How it was obtained"),
):
    """Add a discovered credential."""
    from veinmap.models.credential import add_credential
    valid_types = ("password", "ntlm", "kerberos", "ssh_key", "other")
    if cred_type not in valid_types:
        console.print(f"[red]✗ Invalid type '{cred_type}'. Must be one of: {', '.join(valid_types)}[/]")
        return
    try:
        cred_id = add_credential(username, secret, cred_type, domain, source, method)
        console.print(f"[green]✓ Credential added:[/] {username} (id={cred_id})")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/]")


@cred_app.command("list")
def cred_list(
    cred_type: Optional[str] = typer.Option(None, "--type", "-t"),
    source: Optional[str] = typer.Option(None, "--source", "-s"),
):
    """List all credentials."""
    from veinmap.models.credential import list_credentials
    creds = list_credentials(cred_type, source)
    if not creds:
        console.print("[yellow]No credentials found.[/]")
        return
    tui.print_credentials(creds)


@cred_app.command("test")
def cred_test(
    cred_id: int = typer.Argument(..., help="Credential ID"),
    host_ip: str = typer.Argument(..., help="Host IP tested against"),
    result: str = typer.Argument(..., help="valid|invalid"),
    service: Optional[str] = typer.Option(None, "--service", "-s"),
):
    """Mark a credential as tested against a host."""
    from veinmap.models.credential import mark_tested
    mark_tested(cred_id, host_ip, result, service)
    color = "green" if result == "valid" else "red"
    console.print(f"[{color}]✓ Cred #{cred_id} → {host_ip}: {result}[/]")


@cred_app.command("suggest")
def cred_suggest():
    """Show untested credential/host combinations."""
    from veinmap.models.credential import suggest_untested
    suggestions = suggest_untested()
    tui.print_suggestions(suggestions)


@cred_app.command("import")
def cred_import(
    filepath: str = typer.Argument(..., help="File with user:pass per line"),
    cred_type: str = typer.Option("password", "--type", "-t"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d"),
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Source host IP"),
):
    """Bulk import credentials from a file (user:pass format)."""
    from pathlib import Path
    from veinmap.models.credential import add_credential
    path = Path(filepath)
    if not path.exists():
        console.print(f"[red]✗ File not found: {filepath}[/]")
        return
    count = 0
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(":", 1)
        if len(parts) == 2:
            add_credential(parts[0], parts[1], cred_type, domain, source)
            count += 1
    console.print(f"[green]✓ Imported {count} credentials from {filepath}[/]")


# ═══════════════════════════════════════════
# PIVOT COMMANDS
# ═══════════════════════════════════════════

@pivot_app.command("add")
def pivot_add(
    source_ip: str = typer.Argument(..., help="Pivot source host IP"),
    dest_subnet: str = typer.Argument(..., help="Destination subnet (e.g., 172.16.1.0/24)"),
    method: str = typer.Option(..., "--method", "-m", help="chisel|ligolo|ssh|proxychains"),
    port: Optional[int] = typer.Option(None, "--port", "-p"),
    cmd: Optional[str] = typer.Option(None, "--cmd", "-c", help="Tunnel command used"),
):
    """Add a network pivot."""
    from veinmap.models.pivot import add_pivot
    pid = add_pivot(source_ip, dest_subnet, method, port, cmd)
    if pid:
        console.print(f"[green]✓ Pivot added:[/] {source_ip} → {dest_subnet} via {method}")
    else:
        console.print("[red]✗ Source host not found[/]")


@pivot_app.command("list")
def pivot_list(all: bool = typer.Option(False, "--all", "-a", help="Include closed pivots")):
    """List pivots."""
    from veinmap.models.pivot import list_pivots
    pivots = list_pivots(active_only=not all)
    if not pivots:
        console.print("[yellow]No pivots found.[/]")
        return
    tui.print_pivots(pivots)


@pivot_app.command("close")
def pivot_close(pivot_id: int = typer.Argument(...)):
    """Mark a pivot as closed."""
    from veinmap.models.pivot import close_pivot
    if close_pivot(pivot_id):
        console.print(f"[green]✓ Pivot #{pivot_id} closed[/]")
    else:
        console.print("[red]✗ Pivot not found[/]")


@pivot_app.command("map")
def pivot_map():
    """Display network reachability map."""
    from veinmap.models.pivot import list_pivots
    from rich.tree import Tree
    pivots = list_pivots(active_only=True)
    if not pivots:
        console.print("[yellow]No active pivots. Direct access only.[/]")
        return
    tree = Tree("[bold green]ATTACKER (Kali)[/]")
    # Build reachability from pivot chain
    subnets = {}
    for p in pivots:
        src = p["source_ip"]
        dest = p["destination_subnet"]
        method = p["method"]
        if src not in subnets:
            subnets[src] = []
        subnets[src].append((dest, method, p["local_port"]))

    # First level: direct access (pivots from hosts in first subnet)
    seen = set()
    for p in pivots:
        src = p["source_ip"]
        dest = p["destination_subnet"]
        method = p["method"]
        port_str = f":{p['local_port']}" if p["local_port"] else ""
        label = f"[cyan]{src}[/] → [yellow]{dest}[/] via [green]{method}{port_str}[/]"
        if label not in seen:
            tree.add(label)
            seen.add(label)
    console.print(tree)


# ═══════════════════════════════════════════
# TIMELINE COMMANDS
# ═══════════════════════════════════════════

@timeline_app.command("log")
def timeline_log(
    description: str = typer.Argument(...),
    host: Optional[str] = typer.Option(None, "--host", "-h"),
    category: str = typer.Option("other", "--category", "-c", help="recon|enumeration|exploitation|privesc|lateral|persistence|loot|other"),
    evidence: Optional[str] = typer.Option(None, "--evidence", "-e"),
):
    """Add a timeline entry."""
    from veinmap.models.timeline import add_entry
    valid_cats = ("recon", "enumeration", "exploitation", "privesc", "lateral", "persistence", "loot", "other")
    if category not in valid_cats:
        console.print(f"[red]✗ Invalid category '{category}'. Must be one of: {', '.join(valid_cats)}[/]")
        return
    add_entry(description, host, category, evidence)
    console.print(f"[green]✓ Logged:[/] {description}")


@timeline_app.command("show")
def timeline_show(
    host: Optional[str] = typer.Option(None, "--host", "-h"),
    category: Optional[str] = typer.Option(None, "--category", "-c"),
    limit: int = typer.Option(30, "--limit", "-l"),
):
    """Show timeline entries."""
    from veinmap.models.timeline import list_entries
    entries = list_entries(host, category, limit)
    if not entries:
        console.print("[yellow]No timeline entries.[/]")
        return
    tui.print_timeline(entries)


# ═══════════════════════════════════════════
# FINDING COMMANDS
# ═══════════════════════════════════════════

@finding_app.command("add")
def finding_add(
    title: str = typer.Argument(...),
    severity: str = typer.Option(..., "--severity", "-s", help="critical|high|medium|low|info"),
    host: Optional[List[str]] = typer.Option(None, "--host", "-h", help="Affected host IP(s)"),
    description: Optional[str] = typer.Option(None, "--desc", "-d"),
    impact: Optional[str] = typer.Option(None, "--impact"),
    remediation: Optional[str] = typer.Option(None, "--fix"),
    cvss: Optional[float] = typer.Option(None, "--cvss", help="CVSS score (0.0-10.0)"),
):
    """Add a finding."""
    from veinmap.models.finding import add_finding
    valid_sev = ("critical", "high", "medium", "low", "info")
    if severity not in valid_sev:
        console.print(f"[red]✗ Invalid severity '{severity}'. Must be one of: {', '.join(valid_sev)}[/]")
        return
    if cvss is not None and (cvss < 0 or cvss > 10):
        console.print("[red]✗ CVSS must be between 0.0 and 10.0[/]")
        return
    try:
        fid = add_finding(title, severity, host, description, impact, remediation=remediation, cvss=cvss)
        console.print(f"[green]✓ Finding added:[/] [{severity.upper()}] {title} (id={fid})")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/]")


@finding_app.command("list")
def finding_list(
    severity: Optional[str] = typer.Option(None, "--severity", "-s"),
    host: Optional[str] = typer.Option(None, "--host", "-h"),
):
    """List findings."""
    from veinmap.models.finding import list_findings
    findings = list_findings(severity, host)
    if not findings:
        console.print("[yellow]No findings.[/]")
        return
    tui.print_findings(findings)


@finding_app.command("evidence")
def finding_evidence(
    finding_id: int = typer.Argument(...),
    content: str = typer.Argument(..., help="Evidence text or file path"),
    etype: str = typer.Option("text", "--type", "-t", help="text|screenshot|file"),
    caption: Optional[str] = typer.Option(None, "--caption", "-c"),
):
    """Add evidence to a finding."""
    from veinmap.models.finding import add_evidence
    add_evidence(finding_id, content, etype, caption)
    console.print(f"[green]✓ Evidence added to finding #{finding_id}[/]")


# ═══════════════════════════════════════════
# CHECKLIST COMMANDS
# ═══════════════════════════════════════════

@checklist_app.command("show")
def checklist_show(
    ip: str = typer.Argument(..., help="Host IP"),
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Filter by service"),
):
    """Show checklists for a host."""
    from veinmap.engines.checklist_engine import get_checklist_state, get_checklists_for_host
    if service:
        services = [service]
    else:
        services = get_checklists_for_host(ip)
        if not services:
            console.print("[yellow]No matching checklists. Add ports first or specify --service.[/]")
            return
    for svc in services:
        state = get_checklist_state(ip, svc)
        if state:
            tui.print_checklist(state, ip, svc)


@checklist_app.command("check")
def checklist_check(
    ip: str = typer.Argument(...),
    service: str = typer.Argument(...),
    item_id: str = typer.Argument(...),
):
    """Mark a checklist item as done."""
    from veinmap.engines.checklist_engine import check_item
    if check_item(ip, service, item_id):
        console.print(f"[green]✓ Checked:[/] {item_id}")
    else:
        console.print("[red]✗ Failed — host not found[/]")


@checklist_app.command("uncheck")
def checklist_uncheck(
    ip: str = typer.Argument(...),
    service: str = typer.Argument(...),
    item_id: str = typer.Argument(...),
):
    """Unmark a checklist item."""
    from veinmap.engines.checklist_engine import uncheck_item
    if uncheck_item(ip, service, item_id):
        console.print(f"[yellow]○ Unchecked:[/] {item_id}")


@checklist_app.command("available")
def checklist_available():
    """List available checklists."""
    from veinmap.engines.checklist_engine import get_available_checklists
    checklists = get_available_checklists()
    if not checklists:
        console.print("[yellow]No checklists found in data/checklists/[/]")
        return
    for c in checklists:
        console.print(f"  [green]•[/] {c}")


# ═══════════════════════════════════════════
# REPORT COMMANDS
# ═══════════════════════════════════════════

@report_app.command("generate")
def report_generate(
    template: str = typer.Option("report_cpts.md.j2", "--template", "-t"),
    output: str = typer.Option("report.md", "--output", "-o"),
):
    """Generate pentest report."""
    from veinmap.engines.report_engine import generate_report
    report = generate_report(template, output)
    console.print(f"[green]✓ Report generated:[/] {output} ({len(report)} chars)")


# ═══════════════════════════════════════════
# COMMAND REFERENCE
# ═══════════════════════════════════════════

@cmd_app.command("lookup")
def cmd_lookup(
    query: str = typer.Argument(..., help="Search term (e.g., kerberoast, smb, privesc)"),
    ip: Optional[str] = typer.Option(None, "--ip"),
    user: Optional[str] = typer.Option(None, "--user", "-u"),
    password: Optional[str] = typer.Option(None, "--pass", "-p"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d"),
):
    """Look up commands by technique/service."""
    from veinmap.engines.command_ref import lookup
    results = lookup(query, ip=ip, user=user, password=password, domain=domain)
    if not results:
        console.print(f"[yellow]No commands found for: {query}[/]")
        return
    from rich.panel import Panel
    for r in results:
        console.print(Panel(
            f"[dim]{r['description']}[/]\n\n[green]{r['command']}[/]",
            title=f"[cyan]{r['category']}[/] → {r['section']}",
            border_style="green"
        ))


@cmd_app.command("categories")
def cmd_categories():
    """List available command categories."""
    from veinmap.engines.command_ref import get_available_categories
    for c in get_available_categories():
        console.print(f"  [green]•[/] {c}")


# ═══════════════════════════════════════════
# GLOBAL SEARCH
# ═══════════════════════════════════════════

@app.command()
def search(query: str = typer.Argument(..., help="Search across all data")):
    """Search hosts, credentials, findings, and timeline."""
    from veinmap.db import get_db
    conn = get_db()
    pattern = f"%{query}%"

    hosts = conn.execute("SELECT * FROM hosts WHERE ip LIKE ? OR hostname LIKE ? OR notes LIKE ?",
                         (pattern, pattern, pattern)).fetchall()
    creds = conn.execute("SELECT c.*, h.ip as source_ip FROM credentials c LEFT JOIN hosts h ON c.source_host_id = h.id WHERE c.username LIKE ? OR c.secret LIKE ? OR c.domain LIKE ?",
                         (pattern, pattern, pattern)).fetchall()
    findings = conn.execute("SELECT * FROM findings WHERE title LIKE ? OR description LIKE ?",
                            (pattern, pattern)).fetchall()
    timeline = conn.execute("SELECT t.*, h.ip as host_ip, h.hostname FROM timeline t LEFT JOIN hosts h ON t.host_id = h.id WHERE t.description LIKE ?",
                            (pattern,)).fetchall()
    conn.close()

    if hosts:
        tui.print_hosts(hosts)
    if creds:
        tui.print_credentials(creds)
    if findings:
        tui.print_findings(findings)
    if timeline:
        tui.print_timeline(timeline)
    if not any([hosts, creds, findings, timeline]):
        console.print(f"[yellow]No results for: {query}[/]")


if __name__ == "__main__":
    app()
