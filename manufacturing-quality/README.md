# Manufacturing Quality — PPAP Level 3 Inbox Triage

Triage supplier PPAP Level 3 submission folders by classifying files against the 18 AIAG PPAP elements, flagging gaps, duplicates, and orphan files.

## Quick start

```bash
cd manufacturing-quality
pip install -r requirements.txt
python3 -m ppap_inbox_triage triage fixtures/sample_inbox --output ./triage-out --pdf-text
```

## What it does

1. **Scans** an inbox folder. Immediate subfolders are independent PPAP submissions (18-element review each).
2. **Detects layout** — binder vs discrete vs mixed submission
3. **Classifies** each file to PPAP elements using filename patterns and AIAG semantic PDF content (per-page for binders; table-of-contents pages are skipped)
4. **Triages** completeness, critical gaps, duplicates, and orphans
5. **Writes** JSON, CSV, Markdown triage report, and `sqe-checklist.md` with binder page ranges and evidence terms
6. **Watches** the inbox (optional `watch` command) and re-triages when new supplier files arrive

## Example output

```
[CLARIFY] PPAP Level 3 inbox triage — 83.3% complete
Files: 16 | Missing: 3 | Duplicates: 0 | Orphans: 1
Missing elements: 3, 14, 15
Next action: Confirm physical artifact for element 14 (Sample Production Parts) — documentation not detected in inbox
```

Outputs land in `triage-out/`:

- `triage-report.md` — triage summary with binder page index
- `triage-elements.csv` — spreadsheet with `binder_pages` column
- `triage-report.json` — structured data
- `sqe-checklist.md` — SQE review checklist with page references and sign-off fields

### Watch mode (optional)

Watcher is **not** used when you run `triage` once. Use `watch` to monitor the inbox for new supplier drops:

```bash
python3 -m ppap_inbox_triage watch <inbox_path> --output ./triage-out --pdf-text --layout auto --interval 2
```

Press `Ctrl+C` to stop. Watcher writes the same reports (including `sqe-checklist.md`) on each inbox change.

## Streamlit dashboard (recommended for OneDrive inbox)

**You do not need Git Bash.** Double-click **`Start PPAP Dashboard.vbs`** in File Explorer (most reliable), or `run-dashboard.bat`.

See [WINDOWS-QUICKSTART.md](./WINDOWS-QUICKSTART.md) for troubleshooting. If launch fails, check `dashboard-launch.log` in this folder.

Use **Language / 语言** in the sidebar for English or 中文 labels. Matching always uses both English and Chinese (Simplified and Traditional), including 目录/目錄 pages and Chinese filenames such as `过程FMEA` / `控制计划` / `零件提交保证书`. Scanned image-only PDFs still need OCR.

```bash
# Optional: launch from terminal instead
cd manufacturing-quality
pip install -r requirements.txt
streamlit run dashboard/app.py
```

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
