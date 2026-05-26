# CPTS Engagement Tracker — Full Project Proposal & Design Document

## 1. Project Title

**CPTS Engagement Tracker** — A CLI-based penetration testing workflow assistant for multi-host Active Directory assessments.

## 2. Author

0xmous27

## 3. Date

May 2026

## 4. Version

1.0 (Initial Proposal)

---

## 5. Executive Summary

The CPTS Engagement Tracker is a terminal-based tool designed to solve the organizational challenges faced during timed penetration testing exams (specifically HTB CPTS) and real-world engagements. It provides structured state management for hosts, credentials, network pivots, and findings — then auto-generates a professional pentest report from that data.

Unlike static cheat sheets or generic note-taking tools, this tool actively tracks what you've done, what you've found, and what remains — acting as a second brain during high-pressure, multi-day assessments.

---

## 6. Problem Statement

### 6.1 Context

The HTB Certified Penetration Testing Specialist (CPTS) exam gives candidates:
- A multi-host Active Directory lab environment spanning multiple network segments
- 10 days total (attack phase + report writing phase)
- A requirement to produce a professional-grade penetration testing report

### 6.2 Pain Points

| Problem | Impact |
|---------|--------|
| Losing track of discovered credentials | Missed lateral movement opportunities |
| Forgetting which enumeration steps were completed on which host | Repeated work or skipped attack vectors |
| No clear view of network topology and pivot chains | Confusion about what's reachable |
| Report writing from scratch after exploitation | Hours wasted reconstructing the timeline |
| Fatigue-induced mistakes after 20+ hours | Missed findings, incomplete coverage |
| Scattered notes across multiple files/tools | Context switching overhead |

### 6.3 Gap Analysis

| Existing Tool | What It Does | What It Lacks |
|---------------|-------------|---------------|
| CherryTree / Obsidian | Static note templates | No state tracking, no automation |
| htb-intel (your project) | Command/technique reference | No engagement management |
| Reconmap / Dradis | Enterprise pentest management | Too heavy, not exam-focused, requires server |
| Spreadsheets | Manual tracking | No automation, no report generation, clunky |
| Plain text files | Freeform notes | No structure, easy to lose data |

---

## 7. Specific Objectives

1. Reduce time spent on organization during timed exams by providing structured real-time logging of hosts, credentials, and progress.
2. Eliminate missed enumeration steps through context-aware methodology checklists that adapt per host and service.
3. Centralize credential management so users never lose track of passwords, hashes, or Kerberos tickets across a multi-host environment.
4. Automate report generation by converting logged findings and attack paths into a structured report matching CPTS submission format.
5. Visualize network pivots and attack paths to maintain situational awareness across multiple subnets.
6. Serve as a learning tool where building and populating methodology data reinforces penetration testing knowledge.
7. Provide an open-source community resource for CPTS/OSCP candidates worldwide.

---

## 8. Scope

### 8.1 In Scope

- Host discovery and status tracking
- Credential storage and reuse suggestions
- Per-host, per-service methodology checklists
- Network pivot mapping
- Timestamped attack timeline
- Finding documentation with severity and evidence
- Markdown report generation
- Command reference with variable substitution
- SQLite local storage
- CLI/TUI interface

### 8.2 Out of Scope

- Automated scanning or exploitation (this is a tracker, not a scanner)
- Web-based UI (CLI only for v1)
- Multi-user collaboration
- Cloud sync or remote storage
- Integration with Burp Suite, Metasploit, or other tools (future consideration)

---

## 9. Target Users

| User Type | Use Case |
|-----------|----------|
| CPTS exam candidates | Track progress and generate report during the exam |
| OSCP / OSEP students | Organize lab and exam work |
| Professional pentesters | Lightweight engagement tracking for internal assessments |
| CTF players | Track multi-machine CTF progress |
| Security students | Learn methodology by studying the checklist data |


---

## 10. Functional Requirements

### FR-01: Host Management
- FR-01.1: The system shall allow users to add hosts with: IP address, hostname (optional), OS type, and notes.
- FR-01.2: The system shall allow users to record open ports and identified services per host.
- FR-01.3: The system shall track compromise status per host: `discovered` → `enumerated` → `foothold` → `privilege_escalated` → `owned`.
- FR-01.4: The system shall support tagging hosts by network segment (e.g., DMZ, Internal, Management).
- FR-01.5: The system shall allow editing and deleting hosts.
- FR-01.6: The system shall display a summary table of all hosts with their current status.

### FR-02: Credential Management
- FR-02.1: The system shall store credentials with fields: username, secret, type (password | NTLM hash | Kerberos ticket | SSH key | other), source host, and notes.
- FR-02.2: The system shall track which hosts each credential has been tested against and the result (valid/invalid).
- FR-02.3: The system shall suggest untested credential/host combinations (e.g., "svc_sql:Summer2025! has not been tried on DC01").
- FR-02.4: The system shall allow linking a credential to the finding/method that revealed it.
- FR-02.5: The system shall support bulk import of credentials from a file (user:pass format).
- FR-02.6: The system shall allow searching credentials by username, type, or source.

### FR-03: Methodology Checklists
- FR-03.1: The system shall provide pre-built YAML-defined checklists for services: SMB, LDAP, HTTP/HTTPS, Kerberos, MSSQL, WinRM, SSH, FTP, DNS, RDP, SNMP, SMTP, NFS.
- FR-03.2: The system shall display relevant checklists based on a host's discovered services/ports.
- FR-03.3: The system shall allow users to check/uncheck items per host.
- FR-03.4: Each checklist item shall include: description, command template, and category (enumeration | exploitation | post-exploitation).
- FR-03.5: The system shall support custom user-defined checklist items.
- FR-03.6: The system shall show completion percentage per host.
- FR-03.7: The system shall highlight unchecked high-priority items.

### FR-04: Pivot & Network Tracking
- FR-04.1: The system shall record pivot connections with: source host, destination subnet, method (chisel/ligolo/SSH/proxychains), local port, and status (active/closed).
- FR-04.2: The system shall display a text-based network map showing reachable segments.
- FR-04.3: The system shall store the exact tunnel command used for each pivot (for quick restart).
- FR-04.4: The system shall calculate reachability (which hosts can be reached from current position through pivot chains).

### FR-05: Attack Timeline
- FR-05.1: The system shall auto-log timestamped entries when users perform actions (add host, add cred, change host status, add finding).
- FR-05.2: The system shall allow manual timeline entries with: description, host, category (recon | enum | exploit | privesc | lateral | loot).
- FR-05.3: The system shall support attaching evidence to timeline entries (command output text or file paths to screenshots).
- FR-05.4: The system shall display the timeline in chronological order with filtering by host or category.

### FR-06: Findings Management
- FR-06.1: The system shall allow creating findings with: title, severity (Critical/High/Medium/Low/Informational), description, impact, steps to reproduce, evidence, and remediation.
- FR-06.2: Each finding shall link to one or more affected hosts.
- FR-06.3: The system shall support CVSS scoring (optional field).
- FR-06.4: The system shall allow attaching multiple evidence items per finding (text snippets, file paths).
- FR-06.5: The system shall display findings sorted by severity.

### FR-07: Report Generation
- FR-07.1: The system shall generate a Markdown report from stored data.
- FR-07.2: The report structure shall include:
  - Cover page (engagement name, date, author)
  - Executive Summary (auto-generated from findings count/severity)
  - Scope (auto-populated from host list)
  - Findings (each with description, impact, evidence, remediation)
  - Attack Chain Narrative (from timeline)
  - Remediation Summary (prioritized table)
- FR-07.3: The system shall support custom Jinja2 report templates.
- FR-07.4: The system shall support exporting to PDF (via pandoc or weasyprint if available).
- FR-07.5: The system shall allow regenerating the report at any time with updated data.

### FR-08: Command Reference
- FR-08.1: The system shall include command templates organized by service/technique.
- FR-08.2: Commands shall use placeholders: `{IP}`, `{USER}`, `{PASS}`, `{HASH}`, `{DOMAIN}`, `{PORT}`.
- FR-08.3: The system shall substitute known values from stored hosts/credentials into placeholders.
- FR-08.4: The system shall allow users to add custom command templates.

### FR-09: Data Management
- FR-09.1: The system shall store all data in a local SQLite database.
- FR-09.2: The system shall support creating multiple engagement databases (one per assessment).
- FR-09.3: The system shall support exporting the database for backup/transfer.
- FR-09.4: The system shall support importing data from a previous engagement.

### FR-10: Search & Filter
- FR-10.1: The system shall support global search across all data types (hosts, creds, findings, timeline).
- FR-10.2: The system shall support filtering views by host, severity, status, or service.


---

## 11. Non-Functional Requirements

### NFR-01: Performance
- NFR-01.1: All UI interactions shall respond within 200ms.
- NFR-01.2: The system shall handle engagements with up to 50 hosts, 200 credentials, and 500 timeline entries without degradation.
- NFR-01.3: Report generation shall complete within 5 seconds for a full engagement.

### NFR-02: Portability
- NFR-02.1: The system shall run on Linux, macOS, and Windows with Python 3.9+.
- NFR-02.2: The system shall require zero internet connectivity to function.
- NFR-02.3: The entire tool (code + data) shall be self-contained in a single directory.
- NFR-02.4: The database shall be a single `.db` file that can be copied between machines.

### NFR-03: Usability
- NFR-03.1: The system shall operate entirely in the terminal (no GUI/browser required).
- NFR-03.2: The system shall work over SSH and inside tmux/screen sessions.
- NFR-03.3: The system shall provide `--help` for all commands.
- NFR-03.4: A new user shall be able to add their first host within 2 minutes of installation.
- NFR-03.5: The TUI shall use color coding for severity and status (green=owned, yellow=in-progress, red=critical finding).

### NFR-04: Reliability
- NFR-04.1: The system shall not lose data on unexpected termination (SQLite WAL mode).
- NFR-04.2: The system shall validate all input before database writes.
- NFR-04.3: The system shall handle malformed input gracefully with clear error messages.

### NFR-05: Security
- NFR-05.1: All data shall be stored locally only — no network calls, no telemetry.
- NFR-05.2: The system shall display a warning on first run that credentials are stored in plaintext.
- NFR-05.3: The system shall support optional database encryption (SQLCipher) as a future enhancement.

### NFR-06: Maintainability
- NFR-06.1: The codebase shall follow PEP 8 style guidelines.
- NFR-06.2: All public functions shall have docstrings.
- NFR-06.3: The architecture shall be modular (one module per feature area).
- NFR-06.4: Methodology checklists shall be YAML files editable without code changes.
- NFR-06.5: Report templates shall be Jinja2 files editable without code changes.

### NFR-07: Installability
- NFR-07.1: The system shall install via `pip install .` or `git clone` + `pip install -r requirements.txt`.
- NFR-07.2: Dependencies shall be minimal: Rich, PyYAML, Jinja2, and Python stdlib (sqlite3, datetime, pathlib).
- NFR-07.3: No compiled dependencies or system packages required.

### NFR-08: Extensibility
- NFR-08.1: Community members shall be able to contribute checklist YAML files via pull request without touching core code.
- NFR-08.2: The report template system shall support multiple templates selectable by the user.
- NFR-08.3: The command reference shall be data-driven (JSON/YAML) not hardcoded.

---

## 12. System Architecture

### 12.1 High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                   USER (Terminal)                │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              CLI Layer (Click/Typer)             │
│  Commands: host, cred, checklist, pivot,        │
│            timeline, finding, report, search    │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              TUI Layer (Rich)                    │
│  Tables, panels, progress bars, tree views      │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│            Business Logic Layer                  │
│  HostManager, CredManager, ChecklistEngine,     │
│  PivotTracker, TimelineLogger, FindingManager,  │
│  ReportGenerator, CommandRef                    │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│            Data Access Layer (DAL)              │
│  SQLite via Python sqlite3 stdlib              │
│  Models: Host, Credential, ChecklistItem,       │
│  Pivot, TimelineEntry, Finding, Evidence        │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              Storage Layer                       │
│  engagement.db (SQLite file)                    │
│  data/ (YAML checklists, command refs)          │
│  templates/ (Jinja2 report templates)           │
└─────────────────────────────────────────────────┘
```

### 12.2 Directory Structure

```
cpts-tracker/
├── cpts_tracker/
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point and command definitions
│   ├── tui.py                  # Rich TUI rendering helpers
│   ├── db.py                   # Database connection and schema management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── host.py             # Host dataclass and queries
│   │   ├── credential.py      # Credential dataclass and queries
│   │   ├── checklist.py       # Checklist state tracking
│   │   ├── pivot.py           # Pivot dataclass and queries
│   │   ├── timeline.py        # Timeline entry dataclass and queries
│   │   └── finding.py         # Finding dataclass and queries
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── checklist_engine.py # Loads YAML, manages per-host state
│   │   ├── cred_advisor.py    # Suggests credential reuse
│   │   ├── report_engine.py   # Jinja2 report generation
│   │   └── command_ref.py     # Command lookup and substitution
│   └── utils/
│       ├── __init__.py
│       ├── validators.py      # Input validation
│       └── exporters.py       # DB export/import
├── data/
│   ├── checklists/
│   │   ├── smb.yaml
│   │   ├── ldap.yaml
│   │   ├── http.yaml
│   │   ├── kerberos.yaml
│   │   ├── mssql.yaml
│   │   ├── winrm.yaml
│   │   ├── ssh.yaml
│   │   ├── ftp.yaml
│   │   ├── dns.yaml
│   │   ├── rdp.yaml
│   │   ├── snmp.yaml
│   │   ├── smtp.yaml
│   │   └── nfs.yaml
│   └── commands/
│       ├── enumeration.yaml
│       ├── exploitation.yaml
│       ├── privesc_linux.yaml
│       ├── privesc_windows.yaml
│       ├── lateral_movement.yaml
│       └── ad_attacks.yaml
├── templates/
│   ├── report_cpts.md.j2      # CPTS-format report template
│   ├── report_generic.md.j2   # Generic pentest report template
│   └── executive_summary.md.j2
├── tests/
│   ├── test_host.py
│   ├── test_credential.py
│   ├── test_checklist.py
│   ├── test_report.py
│   └── test_cli.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```


### 12.3 Database Schema

```sql
-- Engagement metadata
CREATE TABLE engagement (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT,
    scope_description TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Hosts
CREATE TABLE hosts (
    id INTEGER PRIMARY KEY,
    ip TEXT NOT NULL UNIQUE,
    hostname TEXT,
    os TEXT,
    network_segment TEXT,
    status TEXT DEFAULT 'discovered' CHECK(status IN ('discovered','enumerated','foothold','privilege_escalated','owned')),
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Ports/Services per host
CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    port INTEGER NOT NULL,
    protocol TEXT DEFAULT 'tcp',
    service_name TEXT,
    version TEXT,
    notes TEXT
);

-- Credentials
CREATE TABLE credentials (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    secret TEXT NOT NULL,
    cred_type TEXT NOT NULL CHECK(cred_type IN ('password','ntlm','kerberos_ticket','ssh_key','other')),
    domain TEXT,
    source_host_id INTEGER REFERENCES hosts(id),
    source_method TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Credential validity mapping
CREATE TABLE cred_host_map (
    id INTEGER PRIMARY KEY,
    credential_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK(status IN ('valid','invalid','untested')),
    service TEXT,
    tested_at TEXT
);

-- Checklist state per host
CREATE TABLE checklist_state (
    id INTEGER PRIMARY KEY,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    checklist_file TEXT NOT NULL,
    item_id TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    notes TEXT
);

-- Pivots
CREATE TABLE pivots (
    id INTEGER PRIMARY KEY,
    source_host_id INTEGER NOT NULL REFERENCES hosts(id),
    destination_subnet TEXT NOT NULL,
    method TEXT NOT NULL,
    local_port INTEGER,
    command TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active','closed')),
    created_at TEXT DEFAULT (datetime('now'))
);

-- Timeline
CREATE TABLE timeline (
    id INTEGER PRIMARY KEY,
    timestamp TEXT DEFAULT (datetime('now')),
    host_id INTEGER REFERENCES hosts(id),
    category TEXT CHECK(category IN ('recon','enumeration','exploitation','privesc','lateral','persistence','loot','other')),
    description TEXT NOT NULL,
    evidence TEXT,
    credential_id INTEGER REFERENCES credentials(id),
    finding_id INTEGER REFERENCES findings(id)
);

-- Findings
CREATE TABLE findings (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('critical','high','medium','low','informational')),
    description TEXT,
    impact TEXT,
    steps_to_reproduce TEXT,
    remediation TEXT,
    cvss_score REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Finding-to-host mapping
CREATE TABLE finding_hosts (
    finding_id INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    PRIMARY KEY (finding_id, host_id)
);

-- Evidence items
CREATE TABLE evidence (
    id INTEGER PRIMARY KEY,
    finding_id INTEGER REFERENCES findings(id) ON DELETE CASCADE,
    timeline_id INTEGER REFERENCES timeline(id),
    evidence_type TEXT CHECK(evidence_type IN ('text','screenshot','file')),
    content TEXT NOT NULL,
    caption TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 13. User Interface Design

### 13.1 CLI Commands

```
cpts-tracker init <name>              # Create new engagement
cpts-tracker use <name>               # Switch active engagement

# Host management
cpts-tracker host add <ip> [--hostname] [--os] [--segment]
cpts-tracker host list [--segment] [--status]
cpts-tracker host status <ip> <new_status>
cpts-tracker host ports <ip> <port:service> [port:service...]
cpts-tracker host info <ip>
cpts-tracker host rm <ip>

# Credential management
cpts-tracker cred add <user> <secret> --type <type> [--source <ip>] [--domain]
cpts-tracker cred list [--type] [--source]
cpts-tracker cred test <cred_id> <host_ip> <result>
cpts-tracker cred suggest                    # Show untested combinations
cpts-tracker cred import <file>

# Methodology checklists
cpts-tracker checklist show <ip> [--service]
cpts-tracker checklist check <ip> <item_id>
cpts-tracker checklist uncheck <ip> <item_id>
cpts-tracker checklist progress [--host <ip>]

# Pivots
cpts-tracker pivot add <source_ip> <dest_subnet> --method <method> [--port] [--cmd]
cpts-tracker pivot list
cpts-tracker pivot close <pivot_id>
cpts-tracker pivot map                       # Show network reachability

# Timeline
cpts-tracker log <description> [--host <ip>] [--category] [--evidence <text>]
cpts-tracker timeline [--host <ip>] [--category] [--last <n>]

# Findings
cpts-tracker finding add <title> --severity <sev> --host <ip> [--description] [--impact] [--remediation]
cpts-tracker finding list [--severity] [--host]
cpts-tracker finding evidence <finding_id> --type <type> --content <content>
cpts-tracker finding show <finding_id>

# Report
cpts-tracker report generate [--template <name>] [--output <path>]
cpts-tracker report preview

# Command reference
cpts-tracker cmd <service_or_technique> [--ip <ip>] [--user <user>] [--pass <pass>]

# Search
cpts-tracker search <query>

# Data management
cpts-tracker export <path>
cpts-tracker import <path>
```

### 13.2 TUI Dashboard (Interactive Mode)

```
cpts-tracker dashboard
```

Launches a Rich-based interactive dashboard:

```
╔══════════════════════════════════════════════════════════════════════╗
║  CPTS ENGAGEMENT TRACKER — Operation: Internal Assessment          ║
║  Started: 2026-05-27 | Elapsed: 14h 32m                           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  HOSTS (7)                          CREDENTIALS (12)               ║
║  ┌────────────┬────────┬────────┐   ┌──────────┬────────┬──────┐  ║
║  │ IP         │ Name   │ Status │   │ User     │ Type   │ From │  ║
║  ├────────────┼────────┼────────┤   ├──────────┼────────┼──────┤  ║
║  │ 10.10.14.1 │ DC01   │ ██████ │   │ svc_sql  │ pass   │ WEB01│  ║
║  │ 10.10.14.5 │ WEB01  │ ██████ │   │ admin    │ ntlm   │ SQL01│  ║
║  │ 10.10.14.8 │ SQL01  │ ████░░ │   │ j.smith  │ pass   │ DC01 │  ║
║  │ 172.16.1.3 │ FILE01 │ ██░░░░ │   └──────────┴────────┴──────┘  ║
║  │ 172.16.1.7 │ DEV01  │ ░░░░░░ │                                  ║
║  └────────────┴────────┴────────┘   PIVOTS (2)                     ║
║                                      Kali → 10.10.14.0/24 (direct) ║
║  PROGRESS                            WEB01 → 172.16.1.0/24 (chisel)║
║  ████████████████░░░░░░░░ 65%                                      ║
║                                      FINDINGS: 3C 2H 1M 0L        ║
║  [h]osts [c]reds [p]ivots [f]indings [t]imeline [r]eport [q]uit   ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 14. Data Flow Diagrams

### 14.1 Core Workflow

```
User discovers host
        │
        ▼
  [host add] ──→ DB: hosts table
        │         Timeline: auto-logged
        ▼
  [host ports] ──→ DB: services table
        │
        ▼
  [checklist show] ──→ Load YAML for matching services
        │                Show unchecked items
        ▼
  User performs enumeration
        │
        ▼
  [checklist check] ──→ DB: checklist_state
  [cred add] ──────────→ DB: credentials
  [log] ───────────────→ DB: timeline
        │
        ▼
  User exploits host
        │
        ▼
  [host status foothold] ──→ DB: hosts.status
  [finding add] ──────────→ DB: findings
  [cred suggest] ─────────→ Query untested combos
        │
        ▼
  User pivots to new network
        │
        ▼
  [pivot add] ──→ DB: pivots table
        │
        ▼
  (Repeat for next host)
        │
        ▼
  [report generate] ──→ Query all tables
                        Apply Jinja2 template
                        Output: report.md
```

### 14.2 Credential Suggestion Flow

```
New credential added
        │
        ▼
  Get all hosts where status != 'owned'
        │
        ▼
  Check cred_host_map for existing tests
        │
        ▼
  Return hosts where status = 'untested'
        │
        ▼
  Display: "Try {user}:{secret} on {host} via {service}"
```


---

## 15. Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Language | Python 3.9+ | Universal on pentest VMs (Kali, Parrot, Ubuntu) |
| CLI Framework | Typer | Modern, type-hinted CLI with auto-help generation |
| TUI Rendering | Rich | Beautiful terminal tables, panels, progress bars |
| Database | SQLite3 (stdlib) | Zero-config, single file, crash-safe with WAL |
| Data Files | PyYAML | Human-readable checklist and command definitions |
| Report Templates | Jinja2 | Flexible, well-known templating engine |
| PDF Export | Pandoc (optional) | Standard Markdown-to-PDF, not a hard dependency |
| Testing | Pytest | Standard Python testing framework |
| Packaging | pyproject.toml | Modern Python packaging standard |

### Dependencies (requirements.txt)

```
typer>=0.9.0
rich>=13.0.0
pyyaml>=6.0
jinja2>=3.1.0
```

Total: 4 dependencies. All well-maintained, widely used, no compiled extensions.

---

## 16. Checklist YAML Format

Example: `data/checklists/smb.yaml`

```yaml
service: smb
ports: [139, 445]
categories:
  enumeration:
    - id: smb_anon_login
      description: "Test anonymous/null session login"
      command: "smbclient -N -L //{IP}"
      priority: high

    - id: smb_enum4linux
      description: "Run enum4linux for full enumeration"
      command: "enum4linux -a {IP}"
      priority: high

    - id: smb_shares_cme
      description: "Enumerate shares with CrackMapExec"
      command: "crackmapexec smb {IP} --shares"
      priority: high

    - id: smb_shares_auth
      description: "Enumerate shares with credentials"
      command: "crackmapexec smb {IP} --shares -u '{USER}' -p '{PASS}'"
      priority: medium

    - id: smb_spider
      description: "Spider readable shares for sensitive files"
      command: "crackmapexec smb {IP} --spider_plus -u '{USER}' -p '{PASS}'"
      priority: medium

    - id: smb_signing
      description: "Check SMB signing (disabled = relay candidate)"
      command: "crackmapexec smb {IP} --gen-relay-list relay.txt"
      priority: high

  exploitation:
    - id: smb_relay
      description: "NTLM relay attack (if signing disabled)"
      command: "ntlmrelayx.py -tf targets.txt -smb2support"
      priority: high

    - id: smb_psexec
      description: "PsExec with valid admin creds"
      command: "impacket-psexec {DOMAIN}/{USER}:{PASS}@{IP}"
      priority: medium

    - id: smb_eternalblue
      description: "Check for MS17-010 (EternalBlue)"
      command: "nmap --script smb-vuln-ms17-010 -p 445 {IP}"
      priority: medium

  post_exploitation:
    - id: smb_secrets_dump
      description: "Dump SAM/LSA/NTDS secrets"
      command: "impacket-secretsdump {DOMAIN}/{USER}:{PASS}@{IP}"
      priority: high
```

---

## 17. Report Template Structure

Example: `templates/report_cpts.md.j2`

```jinja2
# Penetration Test Report

## Engagement: {{ engagement.name }}
**Date:** {{ engagement.start_date }} — {{ engagement.end_date }}
**Assessor:** {{ engagement.client }}

---

## 1. Executive Summary

This assessment identified **{{ findings | selectattr('severity', 'eq', 'critical') | list | length }} critical**, **{{ findings | selectattr('severity', 'eq', 'high') | list | length }} high**, **{{ findings | selectattr('severity', 'eq', 'medium') | list | length }} medium**, and **{{ findings | selectattr('severity', 'eq', 'low') | list | length }} low** severity findings across {{ hosts | length }} hosts.

{{ hosts | selectattr('status', 'eq', 'owned') | list | length }} of {{ hosts | length }} hosts were fully compromised, including Domain Controller access.

---

## 2. Scope

| IP Address | Hostname | OS | Final Status |
|---|---|---|---|
{% for host in hosts %}
| {{ host.ip }} | {{ host.hostname or 'N/A' }} | {{ host.os or 'Unknown' }} | {{ host.status }} |
{% endfor %}

---

## 3. Findings

{% for finding in findings | sort(attribute='severity_order') %}
### 3.{{ loop.index }} [{{ finding.severity | upper }}] {{ finding.title }}

**Affected Hosts:** {{ finding.hosts | join(', ') }}
{% if finding.cvss_score %}**CVSS:** {{ finding.cvss_score }}{% endif %}

**Description:**
{{ finding.description }}

**Impact:**
{{ finding.impact }}

**Steps to Reproduce:**
{{ finding.steps_to_reproduce }}

**Evidence:**
{% for ev in finding.evidence %}
```
{{ ev.content }}
```
{% endfor %}

**Remediation:**
{{ finding.remediation }}

---
{% endfor %}

## 4. Attack Chain Narrative

{% for entry in timeline %}
- **{{ entry.timestamp }}** [{{ entry.category }}] {{ entry.description }}{% if entry.host %} ({{ entry.host.ip }}){% endif %}
{% endfor %}

---

## 5. Remediation Summary

| Priority | Finding | Affected Hosts | Remediation |
|---|---|---|---|
{% for finding in findings | sort(attribute='severity_order') %}
| {{ finding.severity | upper }} | {{ finding.title }} | {{ finding.hosts | join(', ') }} | {{ finding.remediation | truncate(80) }} |
{% endfor %}
```

---

## 18. Implementation Plan

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup (pyproject.toml, directory structure, CI)
- [ ] Database schema implementation and migration system
- [ ] Host management (add, list, status, ports, delete)
- [ ] Basic CLI structure with Typer

### Phase 2: Core Tracking (Week 3-4)
- [ ] Credential management (add, list, test, suggest)
- [ ] Methodology checklist engine (YAML loading, per-host state)
- [ ] Create checklists for top 5 services (SMB, HTTP, LDAP, Kerberos, MSSQL)
- [ ] Timeline logging (auto + manual)

### Phase 3: Network & Findings (Week 5-6)
- [ ] Pivot tracker (add, list, map, close)
- [ ] Finding management (add, evidence, link to hosts)
- [ ] Command reference with variable substitution
- [ ] Global search

### Phase 4: Report & Polish (Week 7-8)
- [ ] Report generator (Jinja2 templates, Markdown output)
- [ ] CPTS-specific report template
- [ ] Interactive TUI dashboard
- [ ] Remaining service checklists (SSH, FTP, DNS, RDP, SNMP, SMTP, NFS, WinRM)

### Phase 5: Release (Week 9-10)
- [ ] Comprehensive testing (unit + integration)
- [ ] Documentation (README, CONTRIBUTING, usage examples)
- [ ] PyPI packaging
- [ ] GitHub release with demo GIF/video
- [ ] Community feedback and iteration

---

## 19. Testing Strategy

| Test Type | Tool | Coverage Target |
|-----------|------|----------------|
| Unit tests | Pytest | All model CRUD operations, checklist loading, command substitution |
| Integration tests | Pytest | CLI commands end-to-end with temp databases |
| Manual testing | Real CPTS-like scenario | Full workflow simulation |

### Key Test Cases
- Add host → verify in DB and timeline auto-logged
- Add credential → verify suggestion engine finds untested hosts
- Complete all checklist items → verify 100% progress
- Generate report with full data → verify all sections populated
- Database survives simulated crash (kill process mid-write)
- Import/export round-trip preserves all data

---

## 20. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Scope creep (adding too many features) | High | Delays release | Strict phase gates, MVP first |
| YAML checklist data incomplete | Medium | Reduced usefulness | Community contributions, iterative improvement |
| Performance issues with large engagements | Low | Poor UX | SQLite indexes, lazy loading |
| Dependency breaking changes | Low | Build failures | Pin exact versions |
| Users store sensitive data insecurely | Medium | Data exposure | Plaintext warning, future encryption option |

---

## 21. Success Metrics

1. **Personal:** Successfully use the tool during CPTS exam and pass
2. **Community:** 50+ GitHub stars within 3 months of release
3. **Utility:** Report generation saves 2+ hours compared to manual writing
4. **Adoption:** At least 5 community-contributed checklist files
5. **Quality:** Zero data loss bugs reported

---

## 22. Future Enhancements (Post v1.0)

- Web UI option (Flask/FastAPI) for those who prefer browser
- Nmap XML import (auto-populate hosts and services)
- BloodHound JSON import (AD relationships)
- Database encryption (SQLCipher)
- Plugin system for custom integrations
- Collaboration mode (shared database via network)
- Integration with htb-intel for command lookups
- AI-assisted finding description generation
- Exam timer with phase reminders

---

## 23. Relationship to htb-intel

| htb-intel | CPTS Engagement Tracker |
|-----------|------------------------|
| Answers: "What technique/command exists?" | Answers: "What have I done and what's next?" |
| Static reference data | Dynamic engagement state |
| Web-based (React) | Terminal-based (Python CLI) |
| Read-only during exam | Read-write during exam |
| Knowledge base | Workflow engine |

**Integration opportunity:** The tracker's command reference could pull from htb-intel's technique database, creating a unified ecosystem where one project feeds the other.

---

## 24. Conclusion

The CPTS Engagement Tracker fills a clear gap between static reference tools and heavyweight enterprise platforms. By focusing on the specific needs of timed pentest exams — state tracking, credential management, methodology enforcement, and automated reporting — it provides immediate practical value while also serving as a deep learning exercise in penetration testing methodology.

Building this tool is itself exam preparation. Using it during the exam is a force multiplier. Sharing it with the community establishes credibility and gives back to the offensive security ecosystem.
