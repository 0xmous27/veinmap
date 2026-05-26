# VeinMap

```
 ██╗   ██╗███████╗██╗███╗   ██╗███╗   ███╗ █████╗ ██████╗
 ██║   ██║██╔════╝██║████╗  ██║████╗ ████║██╔══██╗██╔══██╗
 ██║   ██║█████╗  ██║██╔██╗ ██║██╔████╔██║███████║██████╔╝
 ╚██╗ ██╔╝██╔══╝  ██║██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝
  ╚████╔╝ ███████╗██║██║ ╚████║██║ ╚═╝ ██║██║  ██║██║
   ╚═══╝  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
```

> Mapping the veins of the target.

[![License](https://img.shields.io/badge/license-MIT-00ff99?style=flat-square)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9+-00ff99?style=flat-square)
![Made for](https://img.shields.io/badge/made%20for-CPTS%20%2F%20OSCP%20%2F%20Pentest-red?style=flat-square)

---

## What is VeinMap?

VeinMap is a **CLI-based penetration testing engagement tracker** built for multi-host Active Directory assessments. It tracks hosts, credentials, network pivots, methodology progress, and findings — then auto-generates a professional pentest report from your engagement data.

**Built for the CPTS exam. Useful for any engagement.**

Unlike static cheat sheets or generic note-taking tools, VeinMap actively tracks what you've done, what you've found, and what remains — acting as a second brain during high-pressure, multi-day assessments.

---

## Why VeinMap?

| Problem | VeinMap Solution |
|---------|-----------------|
| Losing track of credentials found hours ago | Credential vault with reuse suggestions |
| Forgetting which enum steps were done on which host | Per-host methodology checklists with progress tracking |
| No clear view of network topology | Pivot tracker with reachability map |
| Report writing from scratch after exploitation | Auto-generated report from engagement data |
| Scattered notes across multiple files | Single source of truth with global search |
| Fatigue-induced mistakes after 20+ hours | Priority-highlighted checklists prevent skipped steps |

---

## Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Host Management** | Track targets, ports, services, OS, segments, and compromise status |
| 🔑 **Credential Vault** | Store creds, track validity per host, get reuse suggestions |
| 📋 **Methodology Checklists** | 13 service-specific YAML checklists with per-host state tracking |
| 🔌 **Pivot Tracker** | Map network tunnels, store commands, visualize reachability |
| ⏱️ **Attack Timeline** | Auto-logged chronological record of your entire engagement |
| 🐛 **Finding Management** | Document vulns with severity, CVSS, evidence, and remediation |
| 📝 **Report Generator** | Jinja2 templates → Markdown report matching CPTS format |
| 🔍 **Command Reference** | Searchable commands with live variable substitution |
| 🔎 **Global Search** | Search across hosts, creds, findings, and timeline |
| 💾 **Multi-Engagement** | Separate databases per assessment, export/import support |

---

## Installation

### Requirements

- Python 3.9+
- No internet required after install
- Works on Linux, macOS, Windows

### Install

```bash
git clone https://github.com/0xmous27/veinmap
cd veinmap
pip install -e .
```

### Verify

```bash
veinmap --help
```

---

## Quick Start

```bash
# 1. Initialize a new engagement
veinmap init cpts_exam

# 2. Add discovered hosts
veinmap host add 10.10.14.5 --hostname DC01 --os "Windows Server 2019" --segment internal
veinmap host add 10.10.14.8 --hostname WEB01 --os "Ubuntu 22.04" --segment dmz

# 3. Add ports/services
veinmap host ports 10.10.14.5 88:kerberos 389:ldap 445:smb 5985:winrm
veinmap host ports 10.10.14.8 22:ssh 80:http 443:http

# 4. Work through methodology checklists
veinmap checklist show 10.10.14.5 --service smb
veinmap checklist check 10.10.14.5 smb smb_null_session

# 5. Log credentials as you find them
veinmap cred add svc_sql 'Summer2025!' --type password --domain corp.local --source 10.10.14.8

# 6. Get suggestions for credential reuse
veinmap cred suggest

# 7. Update host status as you progress
veinmap host status 10.10.14.8 foothold

# 8. Track pivots
veinmap pivot add 10.10.14.8 172.16.1.0/24 --method chisel --port 8080

# 9. Document findings
veinmap finding add "SQL Injection in login" --severity critical --host 10.10.14.8 --desc "Blind SQLi" --fix "Parameterized queries" --cvss 9.8

# 10. Generate your report
veinmap report generate --output report.md
```

---

## Full Command Reference

### Global Commands

```
veinmap init [NAME]           Create new engagement (default: "default")
veinmap use <NAME>            Switch active engagement
veinmap engagements           List all engagements
veinmap export <PATH>         Export current engagement database
veinmap import <PATH>         Import an engagement database
veinmap search <QUERY>        Search across all data types
veinmap --help                Show help
```

---

### Host Management (`veinmap host`)

```
veinmap host add <IP> [OPTIONS]       Add a new target host
  --hostname, -n TEXT                   Hostname
  --os, -o TEXT                         Operating system
  --segment, -s TEXT                    Network segment (e.g., dmz, internal)

veinmap host list [OPTIONS]           List all hosts
  --segment, -s TEXT                    Filter by segment
  --status TEXT                         Filter by status

veinmap host info <IP>                Show detailed host info with services

veinmap host status <IP> <STATUS>     Update compromise status
                                        Values: discovered|enumerated|foothold|privesc|owned

veinmap host ports <IP> <PORTS...>    Add ports/services (format: port:service)
                                        Example: 445:smb 80:http 22:ssh

veinmap host edit <IP> [OPTIONS]      Edit an existing host
  --hostname, -n TEXT                   New hostname
  --os, -o TEXT                         New OS
  --segment, -s TEXT                    New segment
  --notes TEXT                          Notes

veinmap host rm <IP>                  Delete a host
```

**Status progression:**
```
discovered → enumerated → foothold → privesc → owned
```

---

### Credential Management (`veinmap cred`)

```
veinmap cred add <USER> <SECRET> [OPTIONS]    Add a credential
  --type, -t TEXT                               password|ntlm|kerberos|ssh_key|other
  --domain, -d TEXT                             Domain (e.g., corp.local)
  --source, -s TEXT                             Source host IP where it was found
  --method, -m TEXT                             How it was obtained

veinmap cred list [OPTIONS]                   List all credentials
  --type, -t TEXT                               Filter by type
  --source, -s TEXT                             Filter by source host

veinmap cred test <ID> <HOST_IP> <RESULT>     Mark credential tested
                                                Result: valid|invalid
  --service, -s TEXT                            Service tested against

veinmap cred suggest                          Show untested credential/host combos

veinmap cred import <FILE> [OPTIONS]          Bulk import (user:pass per line)
  --type, -t TEXT                               Credential type (default: password)
  --domain, -d TEXT                             Domain for all imported creds
  --source, -s TEXT                             Source host IP
```

**Example credential file (`creds.txt`):**
```
admin:Password123
svc_backup:B@ckup2025!
jsmith:Welcome1
```

---

### Methodology Checklists (`veinmap checklist`)

```
veinmap checklist show <IP> [OPTIONS]         Show checklists for a host
  --service, -s TEXT                            Specific service (auto-detects from ports if omitted)

veinmap checklist check <IP> <SERVICE> <ID>   Mark item as completed

veinmap checklist uncheck <IP> <SERVICE> <ID> Unmark item

veinmap checklist available                   List all available checklists
```

**Available checklists (13 services):**

| Service | Ports | Items |
|---------|-------|-------|
| SMB | 139, 445 | 15 items (enum, exploit, post-exploit) |
| HTTP | 80, 443, 8080, 8443, 8000 | 13 items |
| Kerberos | 88 | 11 items |
| LDAP | 389, 636, 3268 | 10 items |
| MSSQL | 1433 | 9 items |
| WinRM | 5985, 5986 | 6 items |
| SSH | 22 | 7 items |
| FTP | 21 | 6 items |
| DNS | 53 | 6 items |
| RDP | 3389 | 6 items |
| SNMP | 161 | 5 items |
| SMTP | 25, 465, 587 | 6 items |
| NFS | 2049, 111 | 5 items |

**Priority highlighting:**
- 🔴 **HIGH** — Red bold (unchecked critical steps)
- 🟡 **MED** — Yellow (unchecked medium steps)
- ✅ Completed items shown in green

**Adding custom checklists:** Drop a YAML file in `data/checklists/`. See [CONTRIBUTING.md](CONTRIBUTING.md) for format.

---

### Pivot & Network Tracking (`veinmap pivot`)

```
veinmap pivot add <SRC_IP> <DEST_SUBNET> [OPTIONS]    Add a pivot
  --method, -m TEXT (required)                          chisel|ligolo|ssh|proxychains
  --port, -p INT                                        Local port
  --cmd, -c TEXT                                        Full tunnel command (for reference)

veinmap pivot list [OPTIONS]                          List pivots
  --all, -a                                             Include closed pivots

veinmap pivot close <ID>                              Mark pivot as closed

veinmap pivot map                                     Display network reachability tree
```

**Example output of `pivot map`:**
```
ATTACKER (Kali)
├── 10.10.14.8 → 172.16.1.0/24 via chisel:8080
└── 172.16.1.5 → 10.0.0.0/8 via ligolo:11601
```

---

### Attack Timeline (`veinmap timeline`)

```
veinmap timeline log <DESCRIPTION> [OPTIONS]    Add a manual entry
  --host, -h TEXT                                 Associated host IP
  --category, -c TEXT                             recon|enumeration|exploitation|privesc|
                                                  lateral|persistence|loot|other
  --evidence, -e TEXT                             Evidence text or file path

veinmap timeline show [OPTIONS]                 Show timeline
  --host, -h TEXT                                 Filter by host
  --category, -c TEXT                             Filter by category
  --limit, -l INT                                 Max entries (default: 30)
```

**Auto-logged events (no manual action needed):**
- Host discovered
- Host status changed
- Credential found
- Pivot established
- Finding added

---

### Finding Management (`veinmap finding`)

```
veinmap finding add <TITLE> [OPTIONS]           Add a finding
  --severity, -s TEXT (required)                  critical|high|medium|low|info
  --host, -h TEXT (repeatable)                    Affected host IP(s)
  --desc, -d TEXT                                 Description
  --impact TEXT                                   Impact statement
  --fix TEXT                                      Remediation
  --cvss FLOAT                                    CVSS score (0.0-10.0)

veinmap finding list [OPTIONS]                  List findings (sorted by severity)
  --severity, -s TEXT                             Filter by severity
  --host, -h TEXT                                 Filter by host

veinmap finding evidence <ID> <CONTENT>         Add evidence to a finding
  --type, -t TEXT                                 text|screenshot|file
  --caption, -c TEXT                              Evidence caption
```

---

### Report Generation (`veinmap report`)

```
veinmap report generate [OPTIONS]               Generate pentest report
  --template, -t TEXT                             Template name (default: report_cpts.md.j2)
  --output, -o TEXT                               Output file (default: report.md)
```

**Available templates:**
- `report_cpts.md.j2` — Full CPTS-format report (Executive Summary, Scope, Findings, Attack Chain, Remediation)
- `report_generic.md.j2` — Shorter generic pentest report

**Report sections (auto-populated):**
1. Executive Summary (finding counts by severity)
2. Scope (all hosts with status)
3. Findings (sorted by severity, with evidence)
4. Attack Chain Narrative (from timeline)
5. Credentials Discovered
6. Network Pivots
7. Remediation Summary

**Custom templates:** Add `.md.j2` files to `templates/`. Available variables: `hosts`, `findings`, `timeline`, `credentials`, `pivots`, `total_hosts`, `owned_hosts`.

---

### Command Reference (`veinmap cmd`)

```
veinmap cmd lookup <QUERY> [OPTIONS]            Search commands
  --ip TEXT                                       Substitute {IP} placeholder
  --user, -u TEXT                                 Substitute {USER} placeholder
  --pass, -p TEXT                                 Substitute {PASS} placeholder
  --domain, -d TEXT                               Substitute {DOMAIN} placeholder

veinmap cmd categories                          List available command categories
```

**Available categories:**
- `ad_attacks` — BloodHound, Kerberoasting, DCSync, delegation abuse, RBCD
- `enumeration` — Nmap, DNS, SNMP
- `exploitation` — SQLi, LFI, NTLM relay, CVEs
- `lateral_movement` — WMI, PsExec, Evil-WinRM, DCOM, RDP
- `privesc` — Linux (SUID, sudo, cron, capabilities) + Windows (SeImpersonate, services, SAM)

**Example with substitution:**
```bash
$ veinmap cmd lookup kerberoast --ip 10.10.14.5 --user svc_sql --pass 'Summer2025!' --domain corp.local

╭─── ad_attacks → ad_attacks ───╮
│ Kerberoasting                 │
│                               │
│ impacket-GetUserSPNs corp.local/svc_sql:Summer2025! -dc-ip 10.10.14.5 -request │
╰───────────────────────────────╯
```

---

## Data Storage

- **Location:** `~/.veinmap/`
- **Format:** SQLite database (one `.db` file per engagement)
- **Crash-safe:** WAL (Write-Ahead Logging) mode enabled
- **Portable:** Copy the `.db` file to any machine

```
~/.veinmap/
├── .active              # Tracks which engagement is active
├── cpts_exam.db         # Engagement database
├── lab_practice.db      # Another engagement
└── client_pentest.db    # Another engagement
```

---

## Multi-Engagement Workflow

```bash
# Create engagements
veinmap init cpts_exam
veinmap init lab_practice

# Switch between them
veinmap use cpts_exam
veinmap host list          # Shows cpts_exam hosts

veinmap use lab_practice
veinmap host list          # Shows lab_practice hosts

# List all
veinmap engagements

# Backup
veinmap export ~/backup/cpts_exam_backup.db

# Restore on another machine
veinmap import ~/backup/cpts_exam_backup.db --name cpts_exam
```

---

## CPTS Exam Workflow

Recommended workflow for the HTB CPTS exam:

```bash
# Day 1: Setup
veinmap init cpts_may2026

# As you scan
veinmap host add <IP> --hostname <NAME> --os <OS> --segment <SEG>
veinmap host ports <IP> <port:svc> ...

# As you enumerate (follow checklists)
veinmap checklist show <IP> --service smb
veinmap checklist check <IP> smb smb_null_session
# ... work through each service

# As you find creds
veinmap cred add <user> <pass> --type password --domain <dom> --source <IP>
veinmap cred suggest    # What to try next

# As you exploit
veinmap host status <IP> foothold
veinmap timeline log "Got shell via ..." --host <IP> --category exploitation
veinmap finding add "Vuln title" --severity critical --host <IP> --desc "..." --fix "..."

# As you pivot
veinmap pivot add <IP> <subnet> --method chisel --port 8080 --cmd "chisel client ..."

# Day 2: Continue + Report
veinmap report generate --output cpts_report.md
# Edit the markdown, convert to PDF, submit
```

---

## Error Handling

VeinMap validates all inputs and provides clear error messages:

```
✗ Invalid status 'GARBAGE'. Must be one of: discovered, enumerated, foothold, privesc, owned
✗ Invalid type 'FAKETYPE'. Must be one of: password, ntlm, kerberos, ssh_key, other
✗ Invalid severity 'MEGA'. Must be one of: critical, high, medium, low, info
✗ Invalid category 'INVALID'. Must be one of: recon, enumeration, exploitation, ...
✗ Invalid port: 'abc' — must be a number
✗ CVSS must be between 0.0 and 10.0
✗ Host not found: 99.99.99.99
✗ Source host not found
✗ File not found: /path/to/file
✗ Engagement 'name' not found. Run: veinmap init name
✗ Error: UNIQUE constraint failed: hosts.ip
```

---

## Project Structure

```
veinmap/
├── veinmap/                    # Core Python package
│   ├── __init__.py
│   ├── cli.py                  # All CLI commands (Typer)
│   ├── db.py                   # SQLite database layer (WAL mode)
│   ├── tui.py                  # Rich terminal UI (tables, panels, trees)
│   ├── models/                 # Data models (CRUD operations)
│   │   ├── host.py
│   │   ├── credential.py
│   │   ├── pivot.py
│   │   ├── timeline.py
│   │   └── finding.py
│   ├── engines/                # Business logic
│   │   ├── checklist_engine.py # YAML loading, per-host state
│   │   ├── command_ref.py      # Command lookup + substitution
│   │   └── report_engine.py    # Jinja2 report generation
│   └── utils/
├── data/
│   ├── checklists/             # 13 YAML methodology checklists
│   │   ├── smb.yaml
│   │   ├── http.yaml
│   │   ├── kerberos.yaml
│   │   ├── ldap.yaml
│   │   ├── mssql.yaml
│   │   ├── winrm.yaml
│   │   ├── ssh.yaml
│   │   ├── ftp.yaml
│   │   ├── dns.yaml
│   │   ├── rdp.yaml
│   │   ├── snmp.yaml
│   │   ├── smtp.yaml
│   │   └── nfs.yaml
│   └── commands/               # Command reference YAML files
│       ├── ad_attacks.yaml
│       ├── enumeration.yaml
│       ├── exploitation.yaml
│       ├── lateral_movement.yaml
│       └── privesc.yaml
├── templates/                  # Jinja2 report templates
│   ├── report_cpts.md.j2
│   └── report_generic.md.j2
├── tests/                      # Pytest test suite
│   ├── test_host.py
│   ├── test_credential.py
│   ├── test_checklist.py
│   ├── test_report.py
│   └── test_cli.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── PROPOSAL.md
```

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Language | Python 3.9+ | Universal on pentest VMs |
| CLI | Typer | Auto-generated help, type hints |
| TUI | Rich | Beautiful terminal tables, panels, trees |
| Database | SQLite (stdlib) | Zero-config, single file, crash-safe |
| Data | PyYAML | Human-readable checklists/commands |
| Templates | Jinja2 | Flexible report generation |
| Testing | Pytest | Standard Python testing |

**Total dependencies: 4** (typer, rich, pyyaml, jinja2). No compiled extensions.

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding new service checklists
- Adding command references
- Creating report templates
- Code contribution guidelines

---

## Relationship to htb-intel

| [htb-intel](https://htb-intel.vercel.app) | VeinMap |
|---|---|
| Answers: "What technique/command exists?" | Answers: "What have I done and what's next?" |
| Static reference data | Dynamic engagement state |
| Web-based (React) | Terminal-based (Python CLI) |
| Read-only during exam | Read-write during exam |
| Knowledge base | Workflow engine |

They're complementary — htb-intel is your library, VeinMap is your field notebook.

---

## License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

> *"Map the veins. Own the body."* — 0xmous27
