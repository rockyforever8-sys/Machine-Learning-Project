# About Wong — Agent Collaboration Profile

> **Purpose:** Help agent workers collaborate with Wong like a trusted colleague who already knows his context, style, and priorities. Update this file as you learn more. Attach with `@ABOUT-WONG.md` in new chats.

**Last updated:** 2026-08-28 (profile questionnaire completed)

---

## Identity

| Field | Value |
|-------|-------|
| **Name** | Wong |
| **Role** | Data scientist |
| **Organization type** | Supply chain / manufacturing / quality (on-prem) |
| **Primary mission** | Automate agentic workflows across supplier quality, PPAP, FAI, feasibility review, and supply chain operations |
| **Industries served** | Automotive (IATF), medical, humanoid robotics, drones, AI data-storage cooling, industrial & household motion products |

---

## How Wong likes to work

- **Coding style:** Works directly in code to create, debug, and iterate — **Python** is the default language.
- **Communication:** Ask **clarifying questions first** before proposing solutions. Then deliver runnable code, not slides-only answers.
- **Decision making:** Data-first; prototype in Python, then refine toward production integration.
- **Risk tolerance:** Agents may write to production QMS for **non-critical** items; **safety-critical** decisions always require **human sign-off**.
- **Agent tone:** Wong dislikes **over-caution** — be direct, propose concrete next steps, and move forward after clarifying questions are answered. Do not endlessly hedge or refuse to act on non-critical tasks.

---

## Domain focus areas

- [x] Procurement & supplier management (PPAP, supplier quality)
- [x] Quality management (QMS, FAI, SPC, Cpk, CAPA)
- [x] Manufacturing execution (in-house MES)
- [x] Compliance & traceability (IATF, CQI, environmental, IMDS)
- [x] Supply chain contingency & risk mitigation (VUCA)
- [x] Data pipelines & analytics (Python)
- [x] Agent orchestration & MCP integrations (greenfield — nothing connected yet)
- [ ] Inventory & warehouse (secondary)
- [ ] Demand forecasting & S&OP (secondary)

**Current top 3 automation priorities:**

1. **PPAP workflow** — inbox triage, review, reject/accept, reminders, escalation, loop until final approval.
2. **First Article Inspection (FAI)** — compare supplier inspection items vs drawing specs vs in-house measurements; auto Cpk; statistical insights; detect abnormalities and fake data; resolve lab result differences and measurement alignment; quality improvement loop; final approval.
3. **Component feasibility (3-party)** — invite supplier; spec & material review vs requirements/regulations; deviations & improvement proposals; sample timing monitoring; digital signature routing; graph-engineering view of parallel paths to meet product launch.

---

## Technical stack preferences

| Area | Preference |
|------|------------|
| Languages | **Python** (primary) |
| Data | pandas, numpy, scipy/stats; SPC/Cpk libraries as needed |
| Orchestration | Agent workflows; MCP when APIs become available |
| APIs | **Not available today** — systems accessed via exports and UI; design for future API/MCP |
| Auth | On-prem; SSO/TBD when integrations are built |
| Cloud | **On-prem only** — do not assume cloud services |
| Visualization | Graph engineering for parallel process flows (feasibility, sample approval timelines) |

---

## Systems Wong works with

See `SYSTEMS-AND-APIS.md` for full registry.

| System | Purpose | Agent access (today) |
|--------|---------|----------------------|
| **Oracle** | ERP | Exports / UI — read via files initially |
| **In-house MES** | Manufacturing execution | Exports / UI |
| **In-house database / QMS** | Quality records, PPAP, FAI, approvals | Exports / UI; write to prod QMS with policy below |

**Integration status:** No MCP or external tools connected yet. Greenfield — prioritize file-based Python pipelines first, then MCP adapters.

**QMS write policy:**

| Class | Agent behavior |
|-------|----------------|
| Non-critical | May write to production QMS after workflow is validated |
| Safety-critical | Read + recommend only; **human sign-off required** for final disposition |

---

## Three-party review model

Many workflows involve three parties who must align on new component feasibility:

| Party | Role |
|-------|------|
| **Supply chain buyer** | Commercial, sourcing, timing |
| **Supplier quality** | PPAP, FAI, supplier compliance, measurement integrity |
| **Product engineering** | Design intent, specs, DFX requirements |

**DFX dimensions Wong cares about:**

- Design for Manufacturing (DFM)
- Design for Assembly (DFA)
- Design for Reliability (DFR)
- Design for Simplicity, Modularity, Standardization & fungibility
- Design for Sustainability

**Known bottlenecks (organizational, not technical):**

- Weak product design inputs
- Staff capability gaps
- Bureaucratic approval chains
- Communication gaps across the three parties during spec feasibility review

Agents should design workflows that **reduce friction** (clear status, reminders, escalation, parallel-path visibility) without bypassing required approvals.

---

## Compliance & regulations

| Framework / standard | Context |
|---------------------|---------|
| **IATF 16949** | Automotive QMS |
| **CQI-9** | Heat treat system assessment |
| **CQI-11** | Plating system assessment |
| **CQI-12** | Coating system assessment |
| **RoHS** | Restriction of hazardous substances |
| **ELV** | End-of-life vehicle |
| **GADSL** | Global automotive declarable substance list |
| **REACH** | EU chemical registration |
| **IMDS** | International Material Data System |
| **Medical** | Medical device quality requirements (context-specific) |

Product domains: medical, humanoid, drone, AI data-storage cooling, industrial & household motion.

---

## What "good help" looks like

When assisting Wong, agents should:

1. **Ask 1–3 clarifying questions first**, then propose working Python code.
2. **Design for on-prem and file/export ingestion** until APIs exist.
3. **Model approval loops explicitly** — PPAP, FAI, and feasibility all have reject → rework → resubmit cycles.
4. **Include statistical rigor** for FAI (Cpk, control charts, outlier/fake-data detection).
5. **Use graph views** for parallel feasibility and sample-approval timelines.
6. **Respect IATF/CQI/environmental rules** when flagging compliance gaps.
7. **Be decisive** after context is clear — avoid over-caution on non-critical paths.
8. **Capture learnings** — offer to update `LEARNING-LOG.md` after sessions.

When assisting Wong, agents should **not**:

- Assume cloud APIs or SaaS integrations exist (they do not yet).
- Skip human sign-off on safety-critical quality decisions.
- Refuse to proceed on non-critical tasks due to excessive hedging.
- Ignore supplier vs in-house measurement misalignment in FAI workflows.
- Treat PPAP/feasibility as linear — they are **loops** with reminders and escalation.

---

## Interests & passions

- Supply chain **contingency planning** in a **VUCA** world
- Strategy to **mitigate supply risk**
- **Automating supply chain operations** workflows end-to-end
- **Lean manufacturing**
- **Automating quality problem solving** for multiple defects
- **Six Sigma** projects to improve **OEE** (Overall Equipment Effectiveness)

---

## Pet peeves & anti-patterns

- **Over-caution** — asking permission for every trivial step after questions are already answered
- Bureaucracy without automation (reminders, escalation, status visibility should be automated)
- Ignoring parallel paths in feasibility/sample approval (use graph engineering)
- Slide-deck answers without Python prototypes
- Treating supplier data as truth without cross-checking in-house measurements

---

## Glossary (Wong's vocabulary)

| Term | Meaning in Wong's context |
|------|---------------------------|
| **PPAP** | Production Part Approval Process — supplier submission package with loop until approval |
| **FAI** | First Article Inspection — compare supplier vs drawing vs in-house results |
| **Cpk** | Process capability index — auto-calculated in FAI workflows |
| **DFM / DFA / DFR** | Design for Manufacturing / Assembly / Reliability |
| **IMDS** | Material declaration system for automotive environmental compliance |
| **CQI-9/11/12** | AIAG special process assessments (heat treat, plating, coating) |
| **OEE** | Overall Equipment Effectiveness — Six Sigma improvement target |
| **VUCA** | Volatility, Uncertainty, Complexity, Ambiguity — supply chain planning context |
| **3-party review** | Buyer + Supplier Quality + Product Engineering |

---

## Session handoff template

When ending a chat, Wong may say:

> "Update LEARNING-LOG with today's decisions and any new systems we touched."

Agents should append dated entries there and suggest updates to domain docs if facts changed.

---

## Standards & thresholds (confirmed)

| Item | Value |
|------|-------|
| PPAP level | **Level 3** (AIAG) |
| Cpk acceptance | **> 1.67** |
| Drawing specs | **PDF** primary; **PLM export** sometimes |
| Launch milestones | **Spreadsheet** |
| Oracle exports | Format **unknown** — discover from sample file |

## Open items (to resolve in future chats)

- [ ] Notification channel preference (email vs Teams vs in-house) when integrations are added
- [ ] Dev/sandbox QMS environment vs prod-only for agent experiments
- [ ] Oracle: provide sample export so agent can map format
- [ ] Launch spreadsheet: file path, sheet name, column names
- [ ] Digital signature platform for feasibility routing
- [ ] Safety-critical characteristic list (beyond default Cpk > 1.67 rule)
