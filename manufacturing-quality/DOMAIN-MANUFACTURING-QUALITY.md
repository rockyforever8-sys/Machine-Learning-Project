# Manufacturing Quality Domain

## Scope

Supplier **PPAP (Production Part Approval Process)** Level 3 inbox triage for automotive and discrete manufacturing quality engineering.

## PPAP Level 3

Level 3 submission requires documentation for all 18 AIAG PPAP elements unless waived by the customer. Physical samples and checking aids may still be required per the Part Submission Warrant (PSW).

| # | Element | Typical artifacts |
|---|---------|-------------------|
| 1 | Design Records | Drawings, CAD exports, spec sheets |
| 2 | Engineering Change Documents | ECN, ECO, change notices |
| 3 | Customer Engineering Approval | Signed approval, deviation permits |
| 4 | Design FMEA | DFMEA spreadsheets or reports |
| 5 | Process Flow Diagram | PFD, routing flow |
| 6 | Process FMEA | PFMEA |
| 7 | Control Plan | Pre-launch / production control plan |
| 8 | MSA Studies | Gage R&R, bias, linearity |
| 9 | Dimensional Results | Layout inspection, balloon drawings |
| 10 | Material / Performance Test Results | Certs, lab reports, functional test |
| 11 | Initial Process Studies | Cpk/Ppk, SPC capability studies |
| 12 | Qualified Laboratory Documentation | Lab accreditation, scope |
| 13 | Appearance Approval Report | AAR, color/master approval |
| 14 | Sample Production Parts | Sample tag photos, packing lists |
| 15 | Master Sample | Master sample sign-off |
| 16 | Checking Aids | Fixtures, templates, go/no-go |
| 17 | Customer-Specific Requirements | CSR checklists, OEM addenda |
| 18 | Part Submission Warrant | PSW form |

## Inbox Triage Workflow

1. Supplier drops files into an inbox folder (flat or nested).
2. Scanner inventories files and extracts lightweight metadata.
3. **Layout detection** decides whether the submission is a **binder** (one/multi-section PDF), **discrete** (separate element files), or **mixed**.
4. Classifier maps files to PPAP elements using filename patterns and **AIAG semantic content evidence** (per-page for binders). Matching is bilingual (English and Simplified/Traditional Chinese): TOC phrases such as 目录/目錄 are skipped, and PDF text that inserts spaces between Chinese characters is compacted before matching. Table-of-contents / index pages are skipped so a title listing is not treated as the element itself.
5. Triage engine computes completeness, duplicates, and review queue using layout-specific rules.
6. Report generator outputs JSON, CSV, Markdown triage report, and `sqe-checklist.md` with binder page ranges and evidence terms.
7. Watch mode (optional) polls the inbox and re-runs triage when new files stabilize.

### Binder page location (AIAG content, not titles)

For a multi-section PPAP PDF (for example a 137-page Level 3 binder), every page with extractable text is scanned. A page is assigned to an element only when it contains **distinctive AIAG PPAP 4th Edition evidence** for that element (form fields, study metrics, table structure), not merely the element title.

| Rule | Behavior |
|------|----------|
| Table of contents / index | Skipped. A page listing 8+ element titles (or "Table of Contents" / 目录 / 目錄 / 目次) is not an element location. |
| Title-only mention | Not enough to mark an element present. |
| Semantic evidence | Unique markers (e.g. PFMEA + RPN + process step, PSW declaration + submission level, Cpk/Ppk, 过程FMEA + 当前过程控制) locate the actual section. English and Chinese (Simplified/Traditional) are both matched. |
| Section continuation | Following pages that continue the same table/form stay with that element until the next section starts. |
| PSW checklist | The warrant form lists all 18 documents; only element 18 is assigned on that page. |

## Submission Layouts

| Layout | When detected | Assignment rule |
|--------|---------------|-----------------|
| `binder` | Single PPAP PDF, or filename contains "PPAP Level 3", or one PDF covers 3+ elements | One file may satisfy multiple elements; page references recorded |
| `discrete` | 8+ numbered/titled element files | One primary element per file; duplicates flagged across files |
| `mixed` | Binder plus standalone element files | Binder rules for package PDFs; discrete rules for other files |

## Triage Outcomes

- **ready_for_review** — All 18 elements represented; SQE can start formal review.
- **incomplete** — One or more required elements missing.
- **needs_clarification** — Ambiguous filenames, duplicates, or orphan files.
- **blocked** — Critical elements missing (PSW, Control Plan, PFMEA).

## CLI

```bash
# One-shot triage with binder-aware PDF analysis
python -m ppap_inbox_triage triage /path/to/inbox --output ./triage-out --pdf-text --layout auto

# Watch inbox for live supplier drops
python -m ppap_inbox_triage watch /path/to/inbox --output ./triage-out --pdf-text --interval 2
```
