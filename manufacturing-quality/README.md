# Manufacturing Quality — PPAP Level 3 Inbox Triage

Triage supplier PPAP Level 3 submission folders by classifying files against the 18 AIAG PPAP elements, flagging gaps, duplicates, and orphan files.

## Quick start

```bash
cd manufacturing-quality
pip install -r requirements.txt
python3 -m ppap_inbox_triage triage fixtures/sample_inbox --output ./triage-out --pdf-text
```

## What it does

1. **Scans** an inbox folder (recursive by default)
2. **Detects layout** — binder vs discrete vs mixed submission
3. **Classifies** each file to PPAP elements using filename patterns and PDF text (per-page for binders)
4. **Triages** completeness, critical gaps, duplicates, and orphans
5. **Writes** JSON, CSV, and Markdown reports for SQE review
6. **Watches** the inbox and re-triages when new supplier files arrive

## Example output

```
[CLARIFY] PPAP Level 3 inbox triage — 83.3% complete
Files: 16 | Missing: 3 | Duplicates: 0 | Orphans: 1
Missing elements: 3, 14, 15
Next action: Confirm physical artifact for element 14 (Sample Production Parts) — documentation not detected in inbox
```

With `--pdf-text`, ambiguous PDFs can be classified from document content (e.g. a generically named file containing "Customer Engineering Approval").

## CLI

```bash
# One-shot triage (auto-detects binder vs discrete)
python3 -m ppap_inbox_triage triage <inbox_path> [--output DIR] [--pdf-text] [--layout auto|discrete|binder]

# Live watch mode (polls inbox, waits for file stability, re-triages on change)
python3 -m ppap_inbox_triage watch <inbox_path> [--output DIR] [--pdf-text] [--interval 2] [--stable-seconds 1] [--once]
```

## Tests

```bash
cd manufacturing-quality
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
```

## Domain reference

See [DOMAIN-MANUFACTURING-QUALITY.md](./DOMAIN-MANUFACTURING-QUALITY.md) for PPAP element definitions and workflow.
