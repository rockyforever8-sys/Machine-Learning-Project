# Manufacturing & Quality Domain Knowledge

> Attach with `@DOMAIN-MANUFACTURING-QUALITY.md` for MES, QMS, PPAP, FAI, feasibility, and compliance workflows.

**Last updated:** 2026-08-28

---

## Scope (Wong's priorities)

- [x] **PPAP** — full inbox-to-approval loop with reminders and escalation
- [x] **First Article Inspection (FAI)** — multi-source compare, Cpk, anomaly/fake-data detection
- [x] **Component feasibility** — 3-party review with graph-based parallel tracking
- [x] In-process quality (SPC, Cpk)
- [x] Inspection & lab result alignment
- [x] Non-conformance & multi-defect problem solving
- [x] Six Sigma / OEE improvement
- [ ] Batch release (secondary to PPAP/FAI for now)
- [ ] Equipment calibration (document when needed)

---

## Compliance context

| Framework | Applies | Implications for agents |
|-----------|---------|-------------------------|
| **IATF 16949** | Yes | Documented procedures, PPAP, supplier quality, audit records |
| **CQI-9** | Yes | Heat treat — flag when process touches heat treat suppliers |
| **CQI-11** | Yes | Plating |
| **CQI-12** | Yes | Coating |
| **RoHS / ELV / REACH / GADSL** | Yes | Material compliance checks in feasibility review |
| **IMDS** | Yes | Material declarations for automotive environmental compliance |
| **Medical** | Yes (product-dependent) | Stricter traceability where applicable |

**Product domains:** medical, humanoid, drone, AI data-storage cooling, industrial & household motion.

**Validation stance:** Agents assist analysis, routing, reminders, and non-critical QMS updates; **humans sign** safety-critical dispositions and final approvals.

---

## Priority workflow 1: PPAP automation

```
Trigger: new PPAP lands in inbox (QMS or file drop)
→ Triage: completeness vs checklist (IATF PPAP elements)
→ Route to reviewer (supplier quality)
→ Review outcome: Accept | Reject (with reasons) | Hold
→ If reject: notify supplier, set resubmit deadline
→ Reminder job: overdue items
→ Escalation: tiered (reviewer → manager → buyer) based on age/launch risk
→ Loop until final approval recorded
→ Audit log every state transition
```

**Agent capabilities:**

| Step | Automation level |
|------|------------------|
| Inbox triage & checklist | Full auto |
| Gap analysis vs PPAP elements | Full auto |
| Accept/reject recommendation | Auto suggest; human confirm for reject |
| Reminders & escalation | Full auto |
| Final approval | Human sign-off |

---

## Priority workflow 2: First Article Inspection (FAI)

```
Trigger: FAI package submitted (supplier + in-house data available)
→ Ingest: supplier inspection items, drawing specifications, in-house measurements
→ Align: map characteristics across three sources (tolerances, units, datums)
→ Calculate: Cpk per characteristic (Python/scipy)
→ Statistical insights: control limits, trends, capability summary
→ Anomaly detection: outliers, impossible values, duplicate/fake data patterns
→ Lab delta review: flag supplier vs in-house mismatches
→ Resolution loop: measurement alignment proposal → quality improvement actions
→ Route for review → final approval (human for safety-critical)
```

**Fake / abnormal data signals (implement in Python):**

- Values outside physical possibility
- Repeated identical measurements across characteristics
- Cpk inconsistent with raw data distribution
- Supplier pass vs in-house fail on same characteristic
- Missing required characteristics vs drawing

**Output deliverables:**

- Comparison matrix (supplier | drawing | in-house | delta | Cpk)
- Flagged abnormalities with severity
- Recommended disposition (accept / rework / escalate) — **human approves**

---

## Priority workflow 3: Component feasibility (3-party)

```
Trigger: new quoted component / new spec feasibility request
→ Invite supplier to participate
→ Parallel tracks (graph model):
   ├── Supply chain buyer: commercial, timing, sourcing
   ├── Supplier quality: PPAP path, material certs, CQI relevance
   └── Product engineering: DFM, DFA, DFR, simplicity/modularity, sustainability
→ Cross-check vs requirements & regulations (RoHS, REACH, IMDS, etc.)
→ Capture deviations and improvement proposals
→ Monitor sample timing against product launch milestone
→ Route digital signatures per party
→ Graph view: critical path, blocked nodes, overdue parallel branches
→ Escalate when launch date at risk
```

**DFX checklist for agents to verify coverage:**

- [ ] Design for Manufacturing (DFM)
- [ ] Design for Assembly (DFA)
- [ ] Design for Reliability (DFR)
- [ ] Simplicity, modularity, standardization, fungibility
- [ ] Design for Sustainability

**Three parties:**

| Party | Primary concern |
|-------|-----------------|
| Supply chain buyer | Cost, lead time, supplier capacity, launch alignment |
| Supplier quality | PPAP readiness, measurements, material compliance |
| Product engineering | Spec feasibility, DFX, design intent |

---

## Supporting workflows

### Multi-defect quality problem solving

```
Trigger: multiple defects reported (same line/product)
→ Cluster by symptom, station, material lot
→ Pareto + correlation (Python)
→ Draft containment and root-cause hypotheses
→ Link to CAPA template — human owns closure
```

### Six Sigma / OEE

```
Trigger: OEE below target or Six Sigma project charter
→ Pull MES downtime, cycle time, quality loss buckets
→ Quantify improvement opportunity
→ Support DMAIC with data pulls and charts — human leads project
```

---

## Manufacturing entities

| Entity | Key fields | System of record |
|--------|------------|------------------|
| PPAP package | part, supplier, level, status, due date | In-house QMS |
| FAI record | characteristics, Cpk, disposition | In-house QMS |
| Feasibility case | 3-party status, deviations, launch link | In-house QMS |
| Work order | | In-house MES |
| Lab result | measurement, method, equipment | In-house QMS / LIMS |
| Drawing / spec | tolerances, datums | Document management |

---

## Agent guardrails (quality)

1. **Safety-critical FAI / final approval** — recommend only; human signs.
2. **Non-critical QMS updates** (status, reminders, routing) — may write when workflow validated.
3. **Preserve audit trail** — every auto-action logged with timestamp and data snapshot.
4. **On-prem / export-first** — do not assume cloud APIs.
5. **Cross-check supplier data** — never accept supplier-only results without in-house compare.
6. **Model loops** — PPAP and feasibility are iterative, not one-shot.
7. **Ask clarifying questions first** — then act decisively (Wong dislikes over-caution).

---

## Glossary

| Term | Definition |
|------|------------|
| PPAP | Production Part Approval Process |
| FAI | First Article Inspection |
| Cpk | Process capability index |
| NCR | Non-conformance report |
| CAPA | Corrective and preventive action |
| SPC | Statistical process control |
| OEE | Overall Equipment Effectiveness |
| IMDS | International Material Data System |
| CQI | Continuous Quality Initiative (AIAG special processes) |

---

## Open questions

- [ ] PPAP level (1–5) distribution and element checklist version
- [ ] FAI Cpk acceptance thresholds per characteristic type
- [ ] Drawing extraction format (PDF OCR vs structured BOM)
- [ ] Digital signature product for feasibility routing
