# Supply Chain Domain Knowledge

> Attach with `@DOMAIN-SUPPLY-CHAIN.md` for planning, logistics, procurement, and inventory workflows.

---

## Scope

Processes Wong automates in supply chain:

- [ ] Demand forecasting & S&OP
- [ ] Purchase order lifecycle
- [ ] Supplier performance & risk
- [ ] Inbound / outbound logistics
- [ ] Inventory optimization
- [ ] Exception management (shortages, delays)

---

## Key metrics & definitions

| Metric | Definition | Source system |
|--------|------------|---------------|
| OTIF | On-time in-full delivery | |
| DOS | Days of supply | |
| Fill rate | | |
| Lead time | | |

---

## Common workflow patterns

### 1. Exception triage (shortage / delay)

```
Trigger: alert or daily report
→ Pull open POs + inventory + demand
→ Classify severity (line stop vs buffer)
→ Draft recommendation (expedite, substitute, reschedule)
→ Notify owner (Slack / email)
→ Log decision in LEARNING-LOG
```

### 2. Supplier risk check

```
Trigger: new PO or periodic review
→ Fetch supplier scorecard + open issues
→ Cross-check certifications / audit dates
→ Flag if threshold breached
→ Optional: hold PO pending approval
```

### 3. Inventory health snapshot

```
Trigger: scheduled
→ Aggregate by SKU / location
→ Compare to min/max or safety stock
→ Output exceptions list + suggested actions
```

---

## Data entities (map to your ERP)

| Entity | Key fields | Notes |
|--------|------------|-------|
| Purchase order | PO number, vendor, lines, dates | |
| ASN | | |
| SKU / material | | |
| Location / plant | | |

---

## Agent guardrails (supply chain)

- Do not auto-approve POs above `$<!-- threshold -->` without human sign-off.
- Prefer **read-only** queries until workflow is validated.
- Timestamp all recommendations with data-as-of time.
- When systems disagree, surface both values — do not silently merge.

---

## Open questions / to document

- 
- 
