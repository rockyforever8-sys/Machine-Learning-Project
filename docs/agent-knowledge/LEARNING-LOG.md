# Learning Log — Agent Memory Over Time

> Append-only log of decisions, gotchas, and wins. Agents should update this when Wong asks to "capture what we learned."

Format: newest entries at the top.

---

## Template (copy for each entry)

```markdown
### YYYY-MM-DD — [Short title]

**Context:** What we were trying to do  
**Decision:** What we chose  
**Why:** Rationale  
**Gotchas:** What to avoid next time  
**Systems touched:** ERP, Slack, ...  
**Follow-up:** Optional next steps  
```

---

## Entries

### 2026-08-28 — PPAP L3, Cpk, and data source details

**Context:** Follow-up to profile chat — Wong confirmed operational standards and data formats.  
**Decision:** PPAP **Level 3** (AIAG 18-element checklist); FAI Cpk acceptance **> 1.67**; drawings **PDF** (+ PLM export sometimes); launch dates in **spreadsheet**; Oracle export format **unknown** — use sample-file discovery.  
**Why:** Enables PPAP triage checklist and FAI capability rules in Python without re-asking.  
**Gotchas:** PDF tolerance extraction may need OCR for scanned drawings; Oracle schema must not be hard-coded until sample analyzed.  
**Systems touched:** QMS, document management, spreadsheet, Oracle (TBD).  
**Follow-up:** Wong to drop sample Oracle export + launch spreadsheet column map.

### 2026-08-28 — Wong profile questionnaire completed

**Context:** Profile chat — Wong answered systems, priorities, compliance, and working-style questions.  
**Decision:** Documented Oracle + in-house MES + in-house QMS (on-prem, export/UI only); three priority automations: PPAP loop, FAI with Cpk/anomaly detection, 3-party component feasibility with graph engineering.  
**Why:** Gives all future agents accurate context without re-asking basics.  
**Gotchas:** No MCP/tools connected yet — start with Python file pipelines; Wong wants clarifying questions first but dislikes over-caution after that; safety-critical QMS writes need human sign-off only.  
**Systems touched:** Oracle, in-house MES, in-house QMS.  
**Follow-up:** Document Oracle export report names; choose first integration (likely email reminders or folder watch for exports).

### 2026-08-28 — Agent knowledge base initialized

**Context:** Set up personal + domain docs and skills for supply chain / manufacturing automation.  
**Decision:** Use layered model — rules (short), skills (workflows), reference MD (deep context), LEARNING-LOG (evolving memory).  
**Why:** Cursor does not persist chat memory; explicit files give Cloud Agents and new chats consistent context.  
**Gotchas:** `~/.cursor/skills/` is local-only; commit project `.cursor/` for Cloud Agents.  
**Systems touched:** Cursor skills, rules, MCP (planned).  
**Follow-up:** Wong to fill remaining open items in SYSTEMS-AND-APIS.md.

---

<!-- Add new entries above this line -->
