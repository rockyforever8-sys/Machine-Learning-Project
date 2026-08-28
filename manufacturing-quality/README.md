# Manufacturing Quality — PPAP Level 3 Inbox Triage

Triage supplier PPAP Level 3 submission folders by classifying files against the 18 AIAG PPAP elements, flagging gaps, duplicates, and orphan files.

## Quick start

```bash
cd manufacturing-quality
python -m ppap_inbox_triage triage fixtures/sample_inbox --output ./triage-out
```

## What it does

1. **Scans** an inbox folder (recursive by default)
2. **Classifies** each file to PPAP elements using filename patterns
3. **Triages** completeness, critical gaps, duplicates, and orphans
4. **Writes** JSON, CSV, and Markdown reports for SQE review

## Example output

```
[CLARIFY] PPAP Level 3 inbox triage — 83.3% complete
Files: 16 | Missing: 3 | Duplicates: 0 | Orphans: 1
Missing elements: 3, 14, 15
Next action: Request missing critical elements from supplier: ...
```

## CLI

```bash
python -m ppap_inbox_triage triage <inbox_path> [--output DIR] [--no-recursive] [--fail-on-incomplete] [--fail-on-blocked]
```

## Tests

```bash
cd manufacturing-quality
python -m unittest discover -s tests -v
```

## Domain reference

See [DOMAIN-MANUFACTURING-QUALITY.md](./DOMAIN-MANUFACTURING-QUALITY.md) for PPAP element definitions and workflow.
