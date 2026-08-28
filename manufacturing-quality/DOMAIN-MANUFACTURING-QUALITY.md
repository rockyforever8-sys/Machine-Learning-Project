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
3. Classifier maps files to PPAP elements using filename patterns and optional text hints.
4. Triage engine computes completeness, duplicates, and review queue.
5. Report generator outputs JSON, CSV, and Markdown for the SQE inbox.

## Triage Outcomes

- **ready_for_review** — All 18 elements represented; SQE can start formal review.
- **incomplete** — One or more required elements missing.
- **needs_clarification** — Ambiguous filenames, duplicates, or orphan files.
- **blocked** — Critical elements missing (PSW, Control Plan, PFMEA).

## CLI

```bash
python -m ppap_inbox_triage triage /path/to/inbox --output ./triage-out
```
