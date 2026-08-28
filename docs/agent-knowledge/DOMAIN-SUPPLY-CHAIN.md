# Supply Chain Domain Knowledge

> Attach with `@DOMAIN-SUPPLY-CHAIN.md` for planning, procurement, supplier risk, and contingency workflows.

**Last updated:** 2026-08-28

---

## Scope

Processes Wong automates in supply chain:

- [x] **Supplier quality coordination** (PPAP timing, feasibility with buyer)
- [x] **Supply risk mitigation & contingency** (VUCA planning)
- [x] **Automating SC operations workflows** (approvals, reminders, escalation)
- [x] Procurement support (Oracle — export-based today)
- [ ] Demand forecasting & S&OP (secondary)
- [ ] Inbound / outbound logistics (secondary)
- [ ] Inventory optimization (secondary)

---

## Strategic context: VUCA supply chain

Wong's passion area: **contingency planning** when supply is volatile, uncertain, complex, and ambiguous.

Agents should support:

- Scenario modeling (single-source risk, geographic concentration, lead-time buffers)
- Supplier alternates and qualification status linkage to PPAP state
- Early warning when feasibility/PPAP/sample paths threaten **product launch**

---

## Three-party model (supply chain angle)

| Party | SC responsibility |
|-------|-------------------|
| **Supply chain buyer** | Quote evaluation, supplier selection, commercial terms, launch timing |
| **Supplier quality** | PPAP, FAI, compliance evidence |
| **Product engineering** | Spec feasibility, DFX |

**Known bottlenecks agents should design around:**

- Bureaucratic approvals → automate status, reminders, escalation, parallel-path visibility
- Communication gaps → single source of truth in QMS + graph views
- Weak design inputs → flag missing specs early in feasibility

---

## Key metrics & definitions

| Metric | Definition | Source |
|--------|------------|--------|
| OTIF | On-time in-full delivery | Oracle (export) |
| PPAP cycle time | Inbox → final approval | In-house QMS |
| Feasibility cycle time | Request → sample approval | In-house QMS |
| Launch risk days | Slip vs product launch milestone | Program schedule + QMS |
| Supplier qualification | PPAP status + audit certs | QMS + supplier records |

---

## Workflow patterns

### 1. PPAP-driven supplier readiness

```
Trigger: new part for production
→ Check PPAP status in QMS
→ If incomplete: block production release recommendation
→ Coordinate with buyer on launch-critical parts
→ Escalate overdue PPAP tied to launch date
```

### 2. Feasibility & sample timing (launch protection)

```
Trigger: new component quote
→ Start 3-party feasibility (see DOMAIN-MANUFACTURING-QUALITY.md)
→ Graph: parallel paths with milestones
→ Alert buyer when sample approval slips threaten launch
→ Link to contingency options (alternate supplier, redesign)
```

### 3. Supply risk / contingency

```
Trigger: periodic review or disruption event
→ Rank parts by single-source, geography, PPAP status, lead time
→ Cross-reference open feasibility and PPAP gaps
→ Output risk register + mitigation options for Wong
```

### 4. Oracle data ingest (current state)

```
Trigger: scheduled export
→ Python ingest PO, material, supplier master
→ Join to QMS PPAP/FAI status
→ Exception report: parts without approved PPAP near need date
```

---

## Data entities (Oracle + QMS)

| Entity | Key fields | System |
|--------|------------|--------|
| Purchase order | PO, vendor, part, dates | Oracle |
| Material / part | number, description, source | Oracle |
| Supplier | ID, name, certs | Oracle + QMS |
| PPAP | part, supplier, status, due | QMS |
| Feasibility | part, 3-party status, launch link | QMS |
| Launch milestone | product, date | Program / PLM (TBD) |

---

## Agent guardrails (supply chain)

- Do not auto-approve supplier commercial commits — buyer signs.
- Tie escalation to **launch date risk**, not just calendar age.
- Prefer **read-only** Oracle until export mappings are validated.
- Surface PPAP/FAI gaps before recommending production release.
- Design for on-prem exports — no assumed cloud integrations.

---

## Open questions

- [ ] Product launch schedule system of record
- [ ] Supplier scorecard existence and format
- [ ] Contingency plan template Wong uses today
