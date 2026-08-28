---
name: manufacturing-quality
description: |
  Support manufacturing execution and quality workflows: SPC exceptions, CAPA intake,
  batch traceability, inspection data, and audit prep. Use when Wong mentions MES, QMS,
  NCR, CAPA, SPC, lot traceability, batch release, or GxP compliance.
---

# Manufacturing & Quality Workflows

## Prerequisites

- `@DOMAIN-MANUFACTURING-QUALITY.md` in context
- `@SYSTEMS-AND-APIS.md` for MES/QMS access
- Understand compliance tier (ISO, IATF, Part 11, etc.) from domain doc

## Workflow

### 1. Classify request

| Class | Agent may | Agent must not |
|-------|-----------|----------------|
| Analysis / reporting | Read data, summarize, chart | Auto-close CAPA or release batch |
| Drafting | 5-Why skeleton, investigation checklist | Submit as official record without review |
| Integration | Read via MCP, stage transforms | Write to validated prod records without approval |

### 2. Traceability check

For any lot/batch question:

1. Identify system of record (MES vs QMS)
2. Pull genealogy: materials → operations → inspections → deviations
3. Present chain with document IDs and timestamps

### 3. SPC / exception handling

1. Fetch measurement series and control limits
2. Apply agreed rules (document which rules in output)
3. Classify special vs common cause **hypothesis** — label as draft for QE review
4. Suggest investigation steps; do not disposition material

### 4. CAPA assist

1. Gather linked NCRs, lots, equipment (read-only)
2. Search similar historical CAPAs if data available
3. Draft problem statement and containment ideas for human edit

### 5. Output format

Always include:

- **Disclaimer:** "Draft for human review — not an official quality record"
- **Data sources** and retrieval time
- **Gaps** in data that block a complete answer

### 6. Capture

Log compliance-relevant decisions in `LEARNING-LOG.md`. Update domain doc if new SOP references or field maps are discovered.

## Guardrails (non-negotiable)

1. No autonomous write to released records or approved CAPA closures
2. Preserve audit trail — what was read, suggested, and who approved
3. Escalate when spec or procedure is ambiguous
4. Dev/test environments only for agent experiments on QMS writes
