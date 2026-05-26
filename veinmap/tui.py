"""TUI rendering helpers using Rich."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

STATUS_COLORS = {
    "discovered": "white",
    "enumerated": "yellow",
    "foothold": "cyan",
    "privesc": "blue",
    "owned": "green",
}

SEVERITY_COLORS = {
    "critical": "red bold",
    "high": "red",
    "medium": "yellow",
    "low": "blue",
    "info": "white",
}


def print_hosts(hosts):
    table = Table(title="[bold green]HOSTS[/]", border_style="green")
    table.add_column("IP", style="cyan")
    table.add_column("Hostname")
    table.add_column("OS")
    table.add_column("Segment")
    table.add_column("Status")
    for h in hosts:
        color = STATUS_COLORS.get(h["status"], "white")
        table.add_row(h["ip"], h["hostname"] or "-", h["os"] or "-",
                      h["network_segment"] or "-", f"[{color}]{h['status']}[/]")
    console.print(table)


def print_credentials(creds):
    table = Table(title="[bold green]CREDENTIALS[/]", border_style="green")
    table.add_column("ID", style="dim")
    table.add_column("Username", style="cyan")
    table.add_column("Secret")
    table.add_column("Type")
    table.add_column("Domain")
    table.add_column("Source")
    for c in creds:
        table.add_row(str(c["id"]), c["username"], c["secret"],
                      c["cred_type"], c["domain"] or "-", c["source_ip"] or "-")
    console.print(table)


def print_pivots(pivots):
    table = Table(title="[bold green]PIVOTS[/]", border_style="green")
    table.add_column("ID", style="dim")
    table.add_column("Source", style="cyan")
    table.add_column("→ Destination")
    table.add_column("Method")
    table.add_column("Port")
    table.add_column("Status")
    for p in pivots:
        color = "green" if p["status"] == "active" else "red"
        table.add_row(str(p["id"]), p["source_ip"],
                      p["destination_subnet"], p["method"],
                      str(p["local_port"] or "-"), f"[{color}]{p['status']}[/]")
    console.print(table)


def print_timeline(entries):
    table = Table(title="[bold green]TIMELINE[/]", border_style="green")
    table.add_column("Time", style="dim")
    table.add_column("Category")
    table.add_column("Host", style="cyan")
    table.add_column("Description")
    for e in entries:
        table.add_row(e["timestamp"], e["category"] or "-",
                      e["host_ip"] or "-", e["description"])
    console.print(table)


def print_findings(findings):
    table = Table(title="[bold green]FINDINGS[/]", border_style="green")
    table.add_column("ID", style="dim")
    table.add_column("Severity")
    table.add_column("Title")
    table.add_column("CVSS")
    for f in findings:
        color = SEVERITY_COLORS.get(f["severity"], "white")
        table.add_row(str(f["id"]), f"[{color}]{f['severity'].upper()}[/]",
                      f["title"], str(f["cvss_score"] or "-"))
    console.print(table)


def print_checklist(checklist_data, host_ip: str, service: str):
    progress = checklist_data.get("progress", {})
    title = f"[bold green]{service.upper()}[/] on [cyan]{host_ip}[/] — {progress.get('done', 0)}/{progress.get('total', 0)} ({progress.get('percent', 0)}%)"
    table = Table(title=title, border_style="green")
    table.add_column("✓", width=3)
    table.add_column("ID", style="dim")
    table.add_column("Description")
    table.add_column("Command", style="dim")
    table.add_column("Pri", width=4)
    for category, items in checklist_data.get("categories", {}).items():
        table.add_row(f"[bold]─── {category.upper()} ───[/]", "", "", "", "")
        for item in items:
            check = "[green]✓[/]" if item.get("completed") else "[red]○[/]"
            priority = item.get("priority", "medium")
            # Highlight unchecked high-priority items
            if not item.get("completed") and priority == "high":
                desc_style = f"[bold red]{item['description']}[/]"
                pri_style = "[bold red]HIGH[/]"
            elif not item.get("completed") and priority == "medium":
                desc_style = f"[yellow]{item['description']}[/]"
                pri_style = "[yellow]MED[/]"
            else:
                desc_style = item["description"]
                pri_style = priority
            table.add_row(check, item["id"], desc_style, item.get("command", ""), pri_style)
    console.print(table)


def print_suggestions(suggestions):
    if not suggestions:
        console.print("[yellow]No untested credential/host combinations.[/]")
        return
    table = Table(title="[bold yellow]SUGGESTED TESTS[/]", border_style="yellow")
    table.add_column("Credential")
    table.add_column("→ Host")
    for s in suggestions:
        cred_str = f"{s['domain'] + '/' if s['domain'] else ''}{s['username']}:{s['secret']} ({s['cred_type']})"
        host_str = f"{s['ip']}" + (f" ({s['hostname']})" if s["hostname"] else "")
        table.add_row(cred_str, host_str)
    console.print(table)


def banner():
    b = Text("""
 ██╗   ██╗███████╗██╗███╗   ██╗███╗   ███╗ █████╗ ██████╗
 ██║   ██║██╔════╝██║████╗  ██║████╗ ████║██╔══██╗██╔══██╗
 ██║   ██║█████╗  ██║██╔██╗ ██║██╔████╔██║███████║██████╔╝
 ╚██╗ ██╔╝██╔══╝  ██║██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝
  ╚████╔╝ ███████╗██║██║ ╚████║██║ ╚═╝ ██║██║  ██║██║
   ╚═══╝  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
    """, style="green")
    console.print(b)
    console.print("[dim]  Mapping the veins of the target. v0.1.0[/]\n")
