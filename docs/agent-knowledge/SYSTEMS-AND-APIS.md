# Systems & APIs — Integration Registry

> **Purpose:** Single source of truth for platforms Wong's agents connect to. **Never store secrets here** — only env var names and auth patterns.

**Last updated:** 2026-08-28 (Oracle TBD, PDF/PLM drawings, launch spreadsheet)

Attach with `@SYSTEMS-AND-APIS.md` when building or debugging integrations.

---

## Environment summary

| Attribute | Value |
|-----------|-------|
| **Deployment** | On-prem |
| **Integration maturity** | Exports and UI today — **no live APIs or MCP connected yet** |
| **Primary language** | Python |
| **Agent QMS policy** | Write non-critical to prod when validated; human sign-off for safety-critical |

---

## Oracle (ERP)

| Field | Value |
|-------|-------|
| **Vendor / product** | Oracle ERP |
| **Purpose** | ERP — procurement, materials, orders |
| **Environment** | On-prem prod |
| **API type** | **Exports / UI** (no agent API today) |
| **Auth method** | TBD when integrated |
| **Agent access** | Read via scheduled exports; no auto-write until approved |
| **Compliance notes** | Source for PO, material master, supplier links |

**Planned ingestion:**

| Object | Source | Format | Notes |
|--------|--------|--------|-------|
| Purchase orders | Export / report | **Unknown** — Wong to provide sample | Auto-detect CSV/XLS/XML on first drop |
| Material master | Export / report | **Unknown** | Link to PPAP/FAI parts |
| Supplier master | Export / report | **Unknown** | |

**Discovery approach (Oracle format unknown):**

1. Wong drops a sample export into a watch folder
2. Python script sniffs delimiter, encoding, headers (`pandas.read_*` with auto-detect)
3. Document mapped columns in this file after first successful parse

**Rate limits / quirks:**

- On-prem; design file-drop or scheduled export pipelines in Python first.
- Format not yet confirmed — do not hard-code schema until sample is analyzed.

---

## In-house MES

| Field | Value |
|-------|-------|
| **Vendor / product** | In-house (custom) |
| **Purpose** | Manufacturing execution — work orders, operations, production data |
| **Environment** | On-prem prod |
| **API type** | **Exports / UI** |
| **Agent access** | Read via exports; writes require validation |
| **Compliance notes** | Links to lots, operations, OEE data for Six Sigma |

**Key objects:**

| Object | Notes |
|--------|-------|
| Work order | |
| Operation / step | |
| Production counts / downtime | OEE inputs |

---

## In-house database / QMS

| Field | Value |
|-------|-------|
| **Vendor / product** | In-house database (QMS) |
| **Purpose** | PPAP, FAI, approvals, quality records, lab results |
| **Environment** | On-prem prod |
| **API type** | **Exports / UI** (direct DB access possible later — confirm with Wong) |
| **Agent access** | See write policy below |
| **Compliance notes** | IATF 16949, CQI-9/11/12, audit trail required |

**Write policy:**

| Record type | Agent may |
|-------------|-----------|
| Reminders, status updates, non-critical routing | Write after workflow validated |
| PPAP accept/reject (non-safety) | Write with audit log |
| FAI disposition, safety-critical release | **Recommend only — human sign-off** |
| Final approval / digital signature | Human only |

**Key objects:**

| Object | Workflow |
|--------|----------|
| PPAP package | Inbox → review → accept/reject → loop |
| FAI record | Supplier vs drawing vs in-house compare |
| Feasibility review | 3-party spec/material review |
| Lab results | Measurement alignment resolution |
| Approval / signature | Digital routing for feasibility |

---

## Supplier portal / collaboration

| Field | Value |
|-------|-------|
| **Status** | To be integrated — supplier invited into feasibility & PPAP loops |
| **Purpose** | Supplier submissions, deviation proposals, sample timing |
| **Agent access** | TBD — likely email/file ingest initially |

---

## Document management / drawings

| Field | Value |
|-------|-------|
| **Purpose** | Drawing specifications for FAI comparison |
| **Primary format** | **PDF** |
| **Secondary format** | **PLM export** (when available — prefer for structured characteristics) |
| **Agent access** | Read PDF + PLM exports; parse tolerances for FAI compare |
| **Python stack** | `pdfplumber` / `PyMuPDF` for PDF; pandas for PLM CSV/XML exports |

---

## Product launch milestones

| Field | Value |
|-------|-------|
| **System of record** | **Spreadsheet** (Excel or similar) |
| **Purpose** | Product launch dates — link to feasibility sample timing and PPAP escalation |
| **Agent access** | Read via scheduled export or shared file path |
| **Integration** | Join launch date to QMS feasibility/PPAP status for "days to launch" risk scoring |

**Still needed:** spreadsheet file path, sheet name, column names for part/program and launch date.

---

## Communication

| Channel | Status | Used for |
|---------|--------|----------|
| Slack | **Not connected** | Future: alerts, escalations |
| Teams | **Not connected** | Future |
| Email | **Not connected via MCP** | Likely first channel for reminders |
| In-house notification | TBD | PPAP/feasibility reminders |

---

## MCP servers configured

| Server | Status | Used for |
|--------|--------|----------|
| All | **None connected** | Greenfield — build Python file pipelines first, then add MCP |

Config file (when ready): `.cursor/mcp.json`

**Recommended first connections (when Wong approves):**

1. Email MCP or SMTP wrapper — PPAP reminders and escalations
2. Custom MCP for in-house QMS — when API or DB read layer exists
3. File-watch MCP or scheduled folder ingest — Oracle/MES exports

---

## Integration patterns (Wong's environment)

1. **Export → Python ingest → analyze → report** (current default — no API)
2. **Staging table → validate → promote to QMS** (before prod writes)
3. **Human-in-the-loop approve → QMS write** (safety-critical FAI, final approval)
4. **Loop with state machine** — PPAP/FAI/feasibility: pending → review → reject/accept → remind → escalate
5. **Graph model** — parallel feasibility paths with critical-path visibility for launch dates

---

## Data classification

| Class | Examples | Agent rules |
|-------|----------|-------------|
| Public | Published standards (IATF, CQI references) | OK in prompts |
| Internal | Schedules, OTIF, feasibility status | OK in private sessions |
| Confidential | Unreleased product specs, supplier pricing | Minimize in logs |
| Regulated | PPAP, FAI, lab records, IMDS declarations | Audit trail; human sign-off for safety |

---

## Open questions

- [ ] Oracle export report names, cadence, and format (**provide sample file**)
- [ ] Launch milestone spreadsheet path, sheet name, column mapping
- [ ] QMS direct DB access vs export-only
- [ ] Digital signature platform/product
- [ ] Supplier portal mechanics (if any)
- [ ] PLM export format when used (CSV, XML, custom)
