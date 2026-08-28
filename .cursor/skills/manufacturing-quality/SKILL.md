---
name: manufacturing-quality
description: |
  PPAP inbox-to-approval loops, First Article Inspection (FAI) with Cpk and anomaly detection,
  3-party component feasibility with graph parallel paths, IATF/CQI/IMDS compliance checks.
  Use when Wong mentions PPAP, FAI, first article, Cpk, supplier inspection, feasibility review,
  DFM, sample approval, or digital signature routing for quality.
---

# Manufacturing & Quality Workflows (Wong)

## Prerequisites

- `@DOMAIN-MANUFACTURING-QUALITY.md` and `@ABOUT-WONG.md` in context
- `@SYSTEMS-AND-APIS.md` for in-house QMS/MES access patterns
- **Python** for statistics (Cpk, outliers, fake-data heuristics)
- Data via **exports/UI** unless API layer exists

## Wong's top 3 workflows

### 1. PPAP automation

1. Ingest PPAP from QMS inbox or file drop
2. Checklist vs IATF PPAP elements — flag gaps
3. Route to reviewer; recommend accept / reject / hold
4. On reject: notify, set resubmit deadline, **loop**
5. Scheduled reminders → tiered escalation
6. Log every state change; human signs final approval

### 2. FAI automation

1. Ingest **three sources**: supplier inspection, drawing specs, in-house measurements
2. Align characteristics (units, datums, tolerances)
3. **Auto-calculate Cpk** per characteristic (Python)
4. Statistical insights + **anomaly/fake-data detection**
5. Flag lab deltas (supplier vs in-house)
6. Propose measurement alignment and improvement actions
7. Route for review — **human sign-off** if safety-critical

### 3. Component feasibility (3-party)

1. Parties: **buyer**, **supplier quality**, **product engineering**
2. DFX: DFM, DFA, DFR, simplicity/modularity, sustainability
3. Check regulations: RoHS, ELV, REACH, GADSL, IMDS as applicable
4. Track deviations and improvement proposals
5. Monitor sample timing vs **product launch**
6. **Graph engineering** — parallel paths, critical path, blocked nodes
7. Digital signature routing — human executes signatures

## Interaction style

1. Ask **1–3 clarifying questions** before building
2. Then deliver **Python prototypes** — not over-cautious refusal
3. On-prem, export-first — do not assume cloud APIs

## Guardrails

| Action | Policy |
|--------|--------|
| Reminders, status, non-critical routing | Auto OK when validated |
| PPAP reject recommendation | Suggest; human confirms reject |
| FAI safety-critical disposition | Recommend only |
| Final approval / signature | Human only |
| Supplier data | Always cross-check in-house |

## Capture

Offer to update `LEARNING-LOG.md` with field mappings, thresholds, and export formats discovered.
