# Systems & APIs — Integration Registry

> **Purpose:** Single source of truth for platforms Wong's agents connect to. **Never store secrets here** — only env var names and auth patterns.

Attach with `@SYSTEMS-AND-APIS.md` when building or debugging integrations.

---

## Registry template (copy per system)

### [System Name]

| Field | Value |
|-------|-------|
| **Vendor / product** | |
| **Purpose** | e.g. ERP, MES, QMS, WMS, TMS |
| **Environment** | prod / staging / sandbox |
| **Base URL** | `https://...` |
| **API type** | REST / OData / SOAP / GraphQL / file drop |
| **Auth method** | OAuth2 / API key / cert / SSO |
| **Env vars** | `SYSTEM_X_API_KEY`, `SYSTEM_X_BASE_URL` |
| **MCP server** | Built-in name / custom / none |
| **Agent access** | read-only / read-write / human-approved writes |
| **Owner / support** | team or person |
| **Compliance notes** | audit log, validation, Part 11, etc. |

**Key endpoints / objects:**

| Object | Endpoint or table | Notes |
|--------|-------------------|-------|
| | | |

**Rate limits / quirks:**

- 

---

## Systems (fill in)

### ERP

<!-- duplicate template above -->

### MES

### QMS

### WMS / Inventory

### Planning / APS

### Supplier portal

### Document management

### Communication (Slack, Teams, email)

---

## MCP servers configured

| Server | Namespace | Status | Used for |
|--------|-----------|--------|----------|
| Slack | Slack | | alerts, approvals |
| Notion | Notion | | knowledge base |
| Composio | Composio | | multi-app orchestration |
| <!-- custom --> | | | |

Config file: `.cursor/mcp.json` (project) or Cursor Settings → MCP (global).

---

## Integration patterns Wong uses

1. **Read → analyze → recommend** (safe default for new workflows)
2. **Read → transform → write to staging** (validate before prod)
3. **Human-in-the-loop approve → write to prod** (QMS, batch release)
4. **Scheduled sync** (nightly master data, inventory snapshots)
5. **Event-driven** (webhook → agent → action)

---

## Data classification

| Class | Examples | Agent rules |
|-------|----------|-------------|
| Public | marketing, published specs | OK to use in prompts |
| Internal | schedules, KPIs | OK in private agent sessions |
| Confidential | supplier pricing, unreleased products | Minimize in logs; no external LLM if policy requires |
| Regulated | batch records, CAPA, patient safety | Strict audit; human approval for writes |
