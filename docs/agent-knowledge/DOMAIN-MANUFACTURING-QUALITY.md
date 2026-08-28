# Manufacturing & Quality Domain Knowledge

> Attach with `@DOMAIN-MANUFACTURING-QUALITY.md` for MES, QMS, SPC, CAPA, and compliance workflows.

---

## Scope

- [ ] Production scheduling & execution
- [ ] Batch / lot traceability
- [ ] In-process quality (SPC)
- [ ] Inspection & test results
- [ ] Non-conformance & CAPA
- [ ] Equipment calibration
- [ ] Audit preparation

---

## Compliance context

| Framework | Applies? | Implications for agents |
|-----------|----------|-------------------------|
| ISO 9001 | | documented procedures, records |
| IATF 16949 | | automotive-specific |
| FDA 21 CFR Part 11 | | electronic records/signatures |
| GxP | | validation, audit trail |
| Other: | | |

**Validation stance:** <!-- e.g. agents assist analysis; humans sign releases -->

---

## Quality workflow patterns

### 1. SPC exception review

```
Trigger: control chart rule violation (Western Electric, etc.)
→ Pull recent measurements + batch context
→ Summarize likely special vs common cause
→ Draft investigation checklist
→ Route to quality engineer (no auto-disposition)
```

### 2. CAPA intake assist

```
Trigger: NCR created
→ Gather linked lots, equipment, operators (read-only)
→ Suggest similar past CAPAs
→ Draft 5-Why skeleton for human edit
→ Never close CAPA without approval
```

### 3. Batch release support

```
Trigger: batch pending release
→ Checklist: tests complete, deviations resolved, signatures
→ Flag gaps only — human performs release
```

---

## Manufacturing entities

| Entity | Key fields | System of record |
|--------|------------|------------------|
| Work order | | MES |
| Batch / lot | | |
| Operation / step | | |
| Inspection lot | | QMS |
| Equipment | | |

---

## Agent guardrails (quality — strict)

1. **No autonomous write** to released batch records or approved CAPA closures.
2. **Preserve audit trail** — log what was read, what was suggested, who approved.
3. **Use validated data paths** only; no scraping production UIs if API exists.
4. **Escalate ambiguity** — when spec is unclear, ask Wong rather than guess.
5. **Separate dev/test from prod** — never use prod QMS for agent experiments.

---

## Glossary

| Term | Definition |
|------|------------|
| NCR | Non-conformance report |
| CAPA | Corrective and preventive action |
| SPC | Statistical process control |
| OOS | Out of specification |
| | |

---

## Open questions / to document

- 
- 
