---
name: aiag-ppap-4th-edition
description: Apply AIAG PPAP 4th Edition rules when triaging supplier submissions, classifying the 18 elements, reviewing PSW/Level 3 packages, or writing SQE checklists. Use for manufacturing quality, PPAP inbox, binder PDFs, and APQP-related questions.
---

# AIAG PPAP 4th Edition — SQE Skill

Operational summary for agents and SQEs. This is **not** a substitute for the official AIAG PPAP 4th Edition manual or customer-specific requirements (CSRs). When the manual and a CSR conflict, **follow the customer**.

## What PPAP is

**Production Part Approval Process (PPAP)** is how a supplier proves that the production process can make parts that meet the customer design record, at the quoted rate, with capable controls.

PPAP sits on top of **APQP**. Related manuals: AIAG FMEA, MSA, SPC, APQP/Control Plan. IATF 16949 expects PPAP (or equivalent) when the customer requires it.

**Goal of approval:** production intent process + production intent tooling + production intent people, not prototype or trial shortcuts (unless the customer authorizes interim approval).

## When PPAP is required

Typical triggers (customer may add more):

- New part / new tooling
- Correction of a discrepancy on a prior submission
- Engineering change to design records, specs, or materials
- Tooling transfer, refurbishment, additional tooling, or capacity tooling
- Process change (method, sequence, inspection, test, packing)
- Sub-supplier or material source change
- Optional construction or material different from the released design
- Tooling inactive 12+ months (or customer threshold)
- Change that affects fit, form, function, durability, or performance

Bulk materials and some commodities have simplified or CSR-defined packages. Do not assume all 18 elements apply until the design record and CSR are checked.

## Significant production run

PPAP evidence must come from a **significant production run**: production tooling, process, environment, and operators; typically **1 to 8 hours**, and **at least 300 consecutive pieces**, unless the customer specifies otherwise.

Parts used for dimensional results, capability, MSA (as applicable), and sample parts should come from this run (or as the customer directs).

## Five submission levels

The **customer** specifies the level. Default in many automotive programs is **Level 3**. Retention means the supplier keeps the record and can produce it on request.

| Level | What the customer typically receives | Supplier retains |
|-------|--------------------------------------|------------------|
| 1 | PSW only (and AAR if appearance item) | Full PPAP |
| 2 | PSW + limited supporting data + samples as requested | Full PPAP |
| 3 | **PSW + complete supporting data + samples as requested** | Full PPAP |
| 4 | PSW + other data defined by the customer | Full PPAP |
| 5 | PSW + complete data **reviewed at the supplier site** | Full PPAP |

**This project's inbox triage defaults to Level 3:** look for all 18 elements unless waived.

## The 18 PPAP elements

Use these as classification and review rules. Physical artifacts (14–16) may be required even when a PDF exists.

| # | Element | What “good” looks like | SQE watch-outs |
|---|---------|------------------------|----------------|
| 1 | Design records | Latest released drawing/CAD/specs; ballooned print for dimensional | Wrong rev; fixture drawings are not design records |
| 2 | Authorized engineering change documents | ECN/ECO incorporated but not yet in the drawing | Missing effectivity; stale change level vs PSW |
| 3 | Customer engineering approval | Signed approval or authorized deviation **when required** | Blanket “N/A” without CSR basis |
| 4 | Design FMEA | DFMEA per FMEA manual; SEV/OCC/DET; actions on high risk | PFMEA labeled as DFMEA; no design function |
| 5 | Process flow diagrams | Incoming → process → inspect → rework → ship | Flow does not match PFMEA/Control Plan ops |
| 6 | Process FMEA | PFMEA for the manufacturing process; special characteristics; process controls | Critical. Title-only / TOC hit is not a PFMEA |
| 7 | Control Plan | Prototype / pre-launch / production as applicable; sampling; reaction plan | Critical. Must align with PFMEA + flow |
| 8 | MSA studies | Gage R&R (and bias/linearity/stability as required) on SC gauges | Study not on the gauge used for the SC |
| 9 | Dimensional results | All design-record characteristics; actual vs spec; OK/not OK | Partial layout; missing balloons |
| 10 | Material / performance tests | Certs, lab reports, functional tests per design record | Out-of-date lots; wrong spec |
| 11 | Initial process studies | Cpk/Ppk (or CSR index) on special characteristics | Charts without index; wrong subgrouping |
| 12 | Qualified laboratory documentation | Lab scope/accreditation covering the test methods | Expired cert; method not in scope |
| 13 | Appearance Approval Report (AAR) | Required for color/grain/appearance items | Skipped on appearance parts |
| 14 | Sample production parts | Actual parts (and tags/packing list) as requested | Physical artifact — PDF is not the part |
| 15 | Master sample | Retained and identified when required | Confused with production samples |
| 16 | Checking aids | Fixtures/templates/gauges certified to design records | Physical artifact; uncalibrated aids |
| 17 | Customer-specific requirements | CSR checklist + evidence (OEM addenda) | Generic ISO cert offered as CSR |
| 18 | Part Submission Warrant (PSW) | Signed warrant; correct part, rev, level, reason, results | Critical. Checklist of 18 on the PSW is **not** those elements |

### Element linkages (do not review in isolation)

```
Design record (1) ─┬─ DFMEA (4)
                   ├─ Dimensional (9) / tests (10)
                   └─ change docs (2) / customer approval (3)

Process flow (5) ── PFMEA (6) ── Control Plan (7)
                         │              │
                         ├─ MSA (8)     ├─ capability (11)
                         └─ special characteristics on all three
```

Mismatch across 5/6/7 is a common reject reason even when each file exists.

## PSW (element 18)

The PSW is the legal/quality declaration for the submission. Review:

- Part name / number / engineering change level
- Shown-on drawing number, additional changes, PO
- Submission reason and **submission level**
- Mold/cavity/process information as applicable
- Results declaration (meets all / does not meet — with explanation)
- Supplier authorized signature and date
- Customer disposition (approved / rejected / interim)

A PSW that lists all 18 documents as “attached” is still **only element 18**. Other elements need their own evidence pages or files.

## Customer disposition

| Disposition | Meaning |
|-------------|---------|
| Approved | Production may ship to the customer per PO/schedule |
| Interim approval | Limited time or quantity; open issues documented; full approval still required |
| Rejected | Correct and resubmit; do not ship production (unless customer directs otherwise) |

Interim approval is not a pass. Track conditions, expiry, and missing elements.

## Retention vs submission

Suppliers generally **retain the full PPAP** for the production life of the part **plus one calendar year**, or per CSR (often longer). Submission level only changes what is **sent** to the customer.

## Binder vs discrete packages

| Package | Typical form | Review method |
|---------|--------------|---------------|
| Discrete | `01_Drawing.pdf`, `06_PFMEA.xlsx`, `18_PSW.pdf` | One primary element per file |
| Binder | Single “PPAP Level 3” PDF (often 100+ pages) | Scan **every page**; ignore TOC; locate sections by content |
| Mixed | Binder + extra files | Binder rules for the package PDF; discrete rules for standalones |

**Never treat a table of contents as the element.** Titles on page 2 of a 137-page binder are not a PFMEA, Control Plan, or PSW.

Content evidence examples:

- PFMEA: process function, failure mode, SEV/OCC/DET, RPN, current process controls
- Control Plan: reaction plan, sample size/frequency, control method
- MSA: Gage R&R, repeatability, reproducibility, %GRR
- Capability: Cpk/Ppk, USL/LSL, subgroup
- PSW: declaration, submission level, supplier authorized signature

## Runtime source of truth

Cursor agents read this `SKILL.md`. The PPAP CLI, binder classifier, and Streamlit dashboard load structured rules from **`rules.json` in this same folder**.

Edit `rules.json` to change classification markers, SQE checks, critical elements, or AIAG rule text. Keep this narrative in sync with that file.

Loader search order:

1. `.cursor/skills/aiag-ppap-4th-edition/rules.json`
2. `manufacturing-quality/skills/aiag-ppap-4th-edition/rules.json`

## How to use this skill in this repo

When classifying or reviewing PPAP inbox files:

1. Identify **submission level** (default Level 3).
2. Treat **each immediate inbox subfolder as an independent submission** with its own 18-element review. Do not mix files across supplier folders.
3. Detect **binder vs discrete vs mixed** inside that folder.
4. Map files/pages to the **18 elements** using AIAG content, not titles.
5. Flag **critical gaps** first: PSW (18), Control Plan (7), PFMEA (6).
6. Call out **physical artifacts** 14–16 even if paperwork exists.
7. Check **5/6/7 consistency** and PSW vs drawing rev.
8. Apply **CSR (17)** before closing “N/A” on 3, 13, 15.

Triage statuses used by this project:

- `ready_for_review` — all 18 represented
- `incomplete` — required elements missing
- `needs_clarification` — duplicates, orphans, weak matches
- `blocked` — critical elements 6, 7, or 18 missing

## Chinese / bilingual binders

Supplier packages are often mixed English and Chinese (Simplified or Traditional). Classification must match **both**:

- Element titles such as 设计记录 / 設計記錄, 过程FMEA / 過程FMEA, 控制计划 / 控制計劃, 零件提交保证书 / 零件提交保證書
- A 目录 / 目錄 / 目次 page is a table of contents — skip it, same as English TOC
- A PSW form listing 1–18 attached documents is **element 18 only**. Do not mark Design Records (or any other element) present or duplicate from that checklist.
- PDF text may insert spaces between Chinese characters; match on compacted text
- Chinese filenames such as `06_过程FMEA.pdf` / `控制计划.xlsx` / `零件提交保证书.pdf` and binder names such as `PPAP第3级提交.pdf`
- Image-only scanned PDFs have no extractable text — OCR is required before classification
- Dashboard UI: Language / 语言 toggle (English / 中文). Matching always uses both languages regardless of the UI toggle.

## Official source

Purchase and use: **AIAG Production Part Approval Process (PPAP), 4th Edition**, plus the applicable OEM CSR. This skill is a working checklist for agents, not licensed AIAG text.
