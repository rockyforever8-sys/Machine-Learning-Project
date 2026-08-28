---
name: supply-chain-orchestration
description: |
  Automate supply chain workflows: PO lifecycle, inventory exceptions, supplier risk,
  logistics alerts, and S&OP support. Use when Wong works on procurement, planning,
  inventory, OTIF, shortages, or supplier automation. Combines domain knowledge with
  MCP/API integrations.
---

# Supply Chain Orchestration

## Prerequisites

- `@DOMAIN-SUPPLY-CHAIN.md` in context
- `@SYSTEMS-AND-APIS.md` for ERP/WMS endpoints
- MCP servers authenticated for required systems

## Workflow

### 1. Clarify the workflow type

| Type | Examples |
|------|----------|
| Exception triage | shortage, late PO, line stop risk |
| Monitoring | daily inventory health, OTIF dashboard |
| Supplier | scorecard, risk flag, audit dates |
| Planning support | demand vs supply gap analysis |

### 2. Confirm access level

- **Read-only analysis** — proceed
- **Writes (PO change, expedite)** — require explicit Wong approval; document in LEARNING-LOG

### 3. Execute

1. Discover MCP tools (`GetDynamicTools`) for relevant systems
2. Pull data with timestamps (note data-as-of)
3. Analyze in code (Python/pandas preferred unless Wong specifies otherwise)
4. Output: summary table + recommended actions + confidence/assumptions
5. If notifications needed: Slack/email via MCP

### 4. Deliverables format

```markdown
## Summary
[1–3 sentences]

## Data as of
[timestamp + sources]

## Findings
[table or bullets]

## Recommended actions
1. ...
2. ...

## Risks / assumptions
- ...
```

### 5. Capture

Offer to update `LEARNING-LOG.md` with decisions and field mappings discovered.

## Guardrails

- No auto-approval of POs above org threshold without human sign-off
- Surface conflicting values from multiple systems — do not silently merge
- Prefer API/MCP over UI scraping
