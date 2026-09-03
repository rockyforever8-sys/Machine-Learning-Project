#!/usr/bin/env python3
"""Generate C-suite Risk Committee presentation: Exxsol D40 supply chain integrity."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# Corporate palette
NAVY = RGBColor(0x00, 0x2B, 0x5C)
TEAL = RGBColor(0x00, 0x7A, 0x87)
SLATE = RGBColor(0x33, 0x41, 0x55)
LIGHT_GRAY = RGBColor(0xF1, 0xF5, 0xF9)
MID_GRAY = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xB9, 0x1C, 0x1C)
AMBER = RGBColor(0xB4, 0x53, 0x09)
GREEN = RGBColor(0x16, 0x65, 0x34)

OUTPUT = Path(__file__).parent / "Exxsol_D40_Supply_Chain_Risk_Committee.pptx"


def set_run_font(run, size=18, bold=False, color=SLATE, name="Calibri"):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_footer(slide, text="Confidential — Risk Committee | Exxsol D40 Supply Chain Integrity"):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(7.05), Inches(9), Inches(0.3))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = text
    set_run_font(run, size=9, color=MID_GRAY)


def add_title_bar(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(1.15)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.55), Inches(0.22), Inches(8.8), Inches(0.55))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    set_run_font(run, size=28, bold=True, color=WHITE)

    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.55), Inches(0.72), Inches(8.8), Inches(0.35))
        stf = sub_box.text_frame
        sp = stf.paragraphs[0]
        srun = sp.add_run()
        srun.text = subtitle
        set_run_font(srun, size=14, color=RGBColor(0xCB, 0xE5, 0xF0))


def add_bullets(slide, items, left=0.65, top=1.45, width=8.7, height=5.5, size=17, spacing=1.15):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP

    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = item[1] if isinstance(item, tuple) else 0
        text = item[0] if isinstance(item, tuple) else item
        run = p.add_run()
        run.text = text
        set_run_font(run, size=size - (2 if p.level else 0), color=SLATE)
        p.space_after = Pt(size * spacing * 0.55)
        p.space_before = Pt(2)


def add_callout(slide, text, left, top, width, height, fill=RGBColor(0xE0, 0xF2, 0xFE), border=TEAL):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = border
    shape.line.width = Pt(1.25)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.1)
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    set_run_font(run, size=14, bold=True, color=NAVY)


def add_table_slide(slide, headers, rows, col_widths):
    rows_n = len(rows) + 1
    cols_n = len(headers)
    table_shape = slide.shapes.add_table(
        rows_n, cols_n, Inches(0.55), Inches(1.55), Inches(9.0), Inches(0.42 * rows_n + 0.3)
    )
    table = table_shape.table

    for i, w in enumerate(col_widths):
        table.columns[i].width = Inches(w)

    for c, header in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for run in p.runs:
                set_run_font(run, size=11, bold=True, color=WHITE)

    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_GRAY
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT if c > 0 else PP_ALIGN.CENTER
                for run in p.runs:
                    set_run_font(run, size=10, color=SLATE)


def slide_title(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(7.5)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()

    accent = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(5.6), Inches(10), Inches(0.08)
    )
    accent.fill.solid()
    accent.fill.fore_color.rgb = TEAL
    accent.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(1.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Exxsol D40 Supply Chain Risk"
    set_run_font(run, size=40, bold=True, color=WHITE)

    p2 = tf.add_paragraph()
    run2 = p2.add_run()
    run2.text = "Quality Assurance, Traceability & Adulteration Controls"
    set_run_font(run2, size=22, color=RGBColor(0xCB, 0xE5, 0xF0))

    meta = slide.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(8.2), Inches(1.2))
    mtf = meta.text_frame
    for line in [
        "Risk Committee Briefing",
        "Industrial Solvent Procurement — Powder Metallurgy Cleaning Application",
        "September 2026",
    ]:
        mp = mtf.add_paragraph() if mtf.paragraphs[0].text else mtf.paragraphs[0]
        if mp.text:
            mp = mtf.add_paragraph()
        mr = mp.add_run()
        mr.text = line
        set_run_font(mr, size=16, color=RGBColor(0xE2, 0xE8, 0xF0))


def slide_executive_summary(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Executive Summary")
    add_bullets(
        slide,
        [
            "Exxsol D40 is a precision-engineered dearomatized hydrocarbon solvent critical to cleaning porous sintered powder metallurgy (PM) components before plating, coating, or assembly.",
            "Rising feedstock costs and Middle East supply volatility have increased incentive for unauthorized traders to adulterate drums — mixing cheaper chemicals (e.g., methylene chloride, methanol) while retaining genuine labels.",
            "Adulteration destroys the narrow distillation profile and flash point that make D40 suitable for PM cleaning — creating fire, HSE, quality, and downstream process failure risks.",
            "Primary defense: authorized distributor sourcing, batch-level Certificate of Analysis (CoA), chain-of-custody traceability, and independent GC-MS verification for critical lots.",
            "Risk Committee decision requested: approve enhanced procurement controls, supplier qualification criteria, and audit/testing budget for solvent integrity assurance.",
        ],
        size=16,
    )
    add_callout(
        slide,
        "Bottom line: A marginally cheaper drum can cost far more in scrap, rework, safety incidents, and regulatory exposure.",
        0.65,
        6.15,
        8.7,
        0.65,
        fill=RGBColor(0xFE, 0xF3, 0xC7),
        border=AMBER,
    )
    add_footer(slide)


def slide_agenda(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Agenda")
    items = [
        ("1.  Business & Technical Context — Why D40 Specifications Matter", 0),
        ("2.  Boiling Range & Aromatic Content — Engineering Rationale", 0),
        ("3.  Supply Chain Risk Landscape & Price Pressure", 0),
        ("4.  Adulteration Threat Model & Operational Impact", 0),
        ("5.  Distributor QC, Traceability & Anti-Counterfeit Controls", 0),
        ("6.  Detection Methods & Recommended Governance Actions", 0),
    ]
    add_bullets(slide, items, top=1.7, size=20, spacing=1.4)
    add_footer(slide)


def slide_business_context(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Business Context", "Why Exxsol D40 Is on the Risk Agenda")
    add_bullets(
        slide,
        [
            "Application: degreasing and precision cleaning of sintered PM parts where porosity traps machining oils, waxes, and cutting fluids.",
            "Process criticality: residual solvent in pores can block plating adhesion, cause coating defects, or promote in-process corrosion.",
            "D40 is selected for: strong solvency, predictable evaporation, low odor/toxicity, and compatibility with metals and many elastomers.",
            "Specification sensitivity: D40 is not a commodity solvent — performance depends on tight control of distillation range, flash point, and aromatic content.",
            "Supply chain complexity: multiple regional distributors, look-alike products (e.g., generic “Isoparaffin D40”), and relabeled drums increase fraud exposure.",
        ],
        size=15,
    )
    add_footer(slide)


def slide_product_profile(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Product Profile — Exxsol D40")
    headers = ["Parameter", "Typical Specification", "Operational Significance"]
    rows = [
        ["Composition", "Dearomatized isoparaffinic hydrocarbon", "Low toxicity; mild to polymers"],
        ["Distillation (IBP–DP)", "~163–187 °C (narrow range)", "Consistent drying; no heavy-end residue in pores"],
        ["Flash point", "~48 °C", "Flammable — requires ignition-source controls"],
        ["Aromatic content", "<0.1% (often <0.001%)", "Low odor; reduced HSE risk; clean surface"],
        ["Density @ 15 °C", "~0.775 g/cm³", "Batch consistency indicator"],
        ["Viscosity @ 25 °C", "~1.28 mm²/s", "Penetration into porous PM geometry"],
        ["KB value (solvency)", "~31", "Controlled removal of oils and greases"],
        ["OEL (8-hr TWA)", "1,200 mg/m³", "~4× higher than white spirit (~300 mg/m³)"],
    ]
    add_table_slide(slide, headers, rows, [1.6, 2.4, 5.0])
    add_footer(slide)


def slide_boiling_range(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(
        slide,
        "Technical Foundation: Boiling Range",
        "Initial Boiling Point (IBP), Dry Point (DP) & Why the Narrow Range Matters",
    )
    add_bullets(
        slide,
        [
            "IBP (Initial Boiling Point): temperature at which the first distillate appears — reflects the lightest, most volatile components.",
            "DP (Dry Point): temperature at which the last liquid evaporates — reflects the heaviest, least volatile components.",
            "Boiling range = DP − IBP. D40’s narrow range (~24 °C) means all components evaporate within a tight temperature window.",
            ("Predictable drying on high-volume lines — no parts drying too fast (condensation/rust risk) or too slow (bottleneck).", 1),
            ("Equipment setpoints (heaters, condensers, vacuum) remain stable — the fluid behaves as a consistent pseudo-single component.", 1),
            ("Critical for PM: wide-range solvents leave heavy ends trapped in pores → sticky/oily residue that standard room-temp drying cannot remove.", 1),
        ],
        top=1.4,
        size=14,
    )
    add_callout(
        slide,
        "Adulteration with low-boiling additives (MC ~40 °C, methanol ~65 °C) collapses this profile — drying becomes unpredictable and residues become inevitable.",
        0.65,
        5.85,
        8.7,
        0.75,
        fill=RGBColor(0xFE, 0xE2, 0xE2),
        border=RED,
    )
    add_footer(slide)


def slide_aromatic_content(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(
        slide,
        "Technical Foundation: Low Aromatic Content",
        "Dearomatization Is a Performance & Safety Requirement, Not Marketing",
    )
    add_bullets(
        slide,
        [
            "Aromatics (benzene, toluene, xylene ring structures) drive odor, toxicity, and aggressive interaction with polymers.",
            "D40 dearomatization (<0.1% aromatics) delivers:",
            ("Worker safety: OEL 1,200 mg/m³ vs. 300 (white spirit) and 200 (kerosene) mg/m³.", 1),
            ("Material compatibility: reduced swelling/cracking risk for O-rings, seals, and plastic bushings on PM assemblies.", 1),
            ("Surface integrity: avoids aromatic film on metal — essential before electroplating, phosphating, PVD, or adhesive bonding.", 1),
            ("Regulatory & ESG alignment: lower VOC toxicity profile supports occupational health commitments.", 1),
            "Adulteration does not preserve this profile — even if aromatics are unchanged, added volatiles alter toxicity, flammability, and certification validity.",
        ],
        top=1.4,
        size=14,
    )
    add_footer(slide)


def slide_d40_vs_d60(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Product Comparison: D40 vs. D60 / D60(S)")
    headers = ["Attribute", "Exxsol D40", "Exxsol D60 / D60(S)"]
    rows = [
        ["Distillation (IBP–DP)", "163–187 °C", "180–210 °C"],
        ["Flash point", "~48 °C (more flammable)", "~68 °C (lower flammability)"],
        ["Evaporation rate", "Faster (relative ~higher)", "Slower (relative rate ~3, n-BuAc=100)"],
        ["KB value", "~31", "~31"],
        ["Aromatic content", "<0.1%", "<0.1%"],
        ["Transport classification", "Flammable liquid", "Often non-DG for transport (regional)"],
        ["Typical use case", "Fast-dry PM cleaning; tight pore evacuation", "Slower dry; higher flash point needs"],
    ]
    add_table_slide(slide, headers, rows, [2.0, 3.5, 3.5])
    add_callout(
        slide,
        "Note: D60(S) is the same product grade with a supplier-specific designation — not a different formulation.",
        0.55,
        5.35,
        8.9,
        0.55,
    )
    add_footer(slide)


def slide_supply_risk(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Supply Chain Risk Landscape")
    add_bullets(
        slide,
        [
            "Geopolitical driver: Middle East conflict (Iran region) has elevated crude and petrochemical feedstock uncertainty.",
            "Manufacturer action: ExxonMobil announced +$0.06/lb price increase for Exxsol D40 (March 2026).",
            "Market transmission: China terminal reference rose ~5.4% (Apr 2026) and continued upward through mid-2026 (~RMB 9,283/t).",
            "Upstream pressure signal: WD-40 reported up to 100% specialty chemical procurement cost spikes — indicating severe feedstock stress.",
            "Risk implication: widening price spreads between genuine D40 and adulterants (MC, methanol, white spirit) increase fraud incentive.",
            "Procurement trap: “Isoparaffin D40” and relabeled drums can appear visually identical to authentic Exxsol product.",
        ],
        size=14,
    )
    add_footer(slide)


def slide_adulteration_threat(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Adulteration Threat Model", "How Unscrupulous Traders Reduce Cost Per Drum")
    add_bullets(
        slide,
        [
            "Motivation: preserve margin under cost pressure by diluting genuine D40 with significantly cheaper solvents.",
            "Common adulterants:",
            ("Methylene chloride (MC) — B.P. ~40 °C; sweet/chloroform-like odor; very low cost.", 1),
            ("Methanol — B.P. ~65 °C; flash point ~12 °C; readily miscible with hydrocarbons.", 1),
            ("White spirit / kerosene — widens boiling range; degrades precision-cleaning performance.", 1),
            "Concealment methods: reuse authentic Exxsol drums and labels; provide falsified or recycled CoA; mask odor with additives.",
            "Detection difficulty: homogeneous mixtures may appear clear and colorless — visual inspection alone is insufficient.",
            "Regulatory status: product adulteration is fraudulent, may breach chemical safety law, and invalidates SDS-based risk assessments.",
        ],
        top=1.4,
        size=14,
    )
    add_footer(slide)


def slide_impact_table(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Impact of Adulteration on Critical Properties")
    headers = ["Property", "Genuine D40", "After MC / Methanol Adulteration", "Business Impact"]
    rows = [
        [
            "Distillation range",
            "163–187 °C (narrow)",
            "Evaporation starts ~40 °C; range widens",
            "Inconsistent drying; pore residue",
        ],
        [
            "Flash point",
            "~48 °C",
            "Effectively lowered (methanol ~12 °C)",
            "Elevated fire/explosion risk",
        ],
        [
            "Aromatic / HSE profile",
            "Certified low-aromatic",
            "Profile invalidated",
            "Worker exposure; compliance breach",
        ],
        [
            "Solvency (KB)",
            "~31 (controlled)",
            "Unpredictable",
            "Cleaning failure or part damage",
        ],
        [
            "Viscosity / wetting",
            "~1.28 mm²/s",
            "Reduced",
            "Poor pore penetration in PM parts",
        ],
        [
            "Downstream processes",
            "Clean, active surface",
            "Contaminated surface",
            "Plating/coating adhesion failure",
        ],
    ]
    add_table_slide(slide, headers, rows, [1.5, 1.7, 2.3, 2.5])
    add_footer(slide)


def slide_operational_risks(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Enterprise Risk Exposure")
    risks = [
        ("Safety & Regulatory", "Undeclared flammable components (methanol) can violate ATEX/fire codes, invalidate SDS, and increase incident severity.", RED),
        ("Product Quality", "Residue in sintered pores → plating peel-off, coating voids, customer complaints, and warranty claims.", AMBER),
        ("Operational", "Unstable distillation → variable cycle times, increased scrap, and unplanned line stoppages.", AMBER),
        ("Financial", "False economy: savings on solvent cost vs. scrap, rework, downtime, and liability exposure.", NAVY),
        ("Reputational", "Supply chain integrity failure with automotive/industrial customers relying on PPAP-level material control.", NAVY),
    ]
    y = 1.5
    for title, body, color in risks:
        shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(y), Inches(8.8), Inches(0.95)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = LIGHT_GRAY
        shape.line.color.rgb = color
        shape.line.width = Pt(2)
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{title}: "
        set_run_font(r1, size=14, bold=True, color=color)
        r2 = p.add_run()
        r2.text = body
        set_run_font(r2, size=13, color=SLATE)
        y += 1.05
    add_footer(slide)


def slide_distributor_controls(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Distributor Quality Control Framework")
    add_bullets(
        slide,
        [
            "Tier 1 — Authorized sourcing only:",
            ("Purchase exclusively through ExxonMobil-verified authorized distributors.", 1),
            ("Maintain current authorization letters and annual re-confirmation with manufacturer.", 1),
            ("Reject “look-alike” products: generic Isoparaffin D40 ≠ Exxsol D40.", 1),
            "Tier 2 — Batch documentation:",
            ("Mandatory batch-specific Certificate of Analysis (CoA) before goods receipt.", 1),
            ("CoA must confirm: distillation IBP/DP, flash point, density, aromatic content, and product identity.", 1),
            ("SDS revision and product code must match purchase order and approved supplier record.", 1),
            "Tier 3 — Physical integrity:",
            ("Tamper-evident seals; drum condition inspection; label hologram/batch cross-check where available.", 1),
            ("Photographic evidence at receipt for critical production lines.", 1),
        ],
        top=1.35,
        size=13,
    )
    add_footer(slide)


def slide_traceability(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Traceability & Chain of Custody")
    add_bullets(
        slide,
        [
            "End-to-end lot tracking: manufacturer batch → distributor invoice → inbound GRN → storage location → dispensing to line.",
            "System requirements:",
            ("ERP/material master locked to approved supplier part numbers only.", 1),
            ("Barcode/QR on drum linked to CoA PDF and receiving inspection record.", 1),
            ("FIFO/FEFO dispensing with lot genealogy traceable to finished part serial/batch.", 1),
            "Supplier audit program:",
            ("Annual distributor quality audit (storage, handling, sub-distribution controls).", 1),
            ("Right-to-audit clause in contracts; penalty clauses for documentation falsification.", 1),
            "Incident response: quarantine protocol for suspect lots; notify manufacturer; retain retain samples per batch.",
        ],
        top=1.4,
        size=14,
    )
    add_callout(
        slide,
        "Traceability converts a chemical purchase into an auditable control — essential for IATF/PPAP material evidence.",
        0.65,
        6.0,
        8.7,
        0.6,
    )
    add_footer(slide)


def slide_detection(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Detection & Verification Controls")
    headers = ["Control", "Method", "Frequency", "Purpose"]
    rows = [
        ["Incoming CoA review", "Spec match vs. ExxonMobil datasheet", "Every batch", "First line of defense"],
        ["On-site screening", "Density, flash point, refractive index", "Risk-based / each lot", "Rapid anomaly flag"],
        ["Odor check (screening)", "D40 = mild; MC = sweet; methanol = alcoholic", "Each drum (trained staff)", "Early warning — not definitive"],
        ["GC-MS analysis", "Independent lab fingerprint", "Critical lots / quarterly", "Definitive adulterant ID"],
        ["Supplier scorecard", "CoA rejection rate, audit findings", "Quarterly", "Continuous improvement"],
        ["Market intelligence", "Price benchmarking vs. authorized list", "Ongoing", "Flags “too good to be true” offers"],
    ]
    add_table_slide(slide, headers, rows, [1.8, 2.8, 1.6, 2.8])
    add_footer(slide)


def slide_recommendations(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Recommended Actions", "Risk Committee Approval Requested")
    actions = [
        ("1", "Approve authorized-distributor-only procurement policy with executive exception process."),
        ("2", "Mandate batch CoA verification and quarantine-until-approved for all D40 receipts."),
        ("3", "Fund independent GC-MS testing program (minimum quarterly + any price anomaly trigger)."),
        ("4", "Implement drum-to-dispense digital traceability in ERP within next planning cycle."),
        ("5", "Conduct distributor audit (storage, labeling, sub-supply controls) within 90 days."),
        ("6", "Brief operations on flash-point and adulteration risks; update chemical risk assessment."),
    ]
    y = 1.55
    for num, text in actions:
        circle = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.OVAL, Inches(0.65), Inches(y), Inches(0.42), Inches(0.42)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = TEAL
        circle.line.fill.background()
        ctf = circle.text_frame
        cp = ctf.paragraphs[0]
        cp.alignment = PP_ALIGN.CENTER
        cr = cp.add_run()
        cr.text = num
        set_run_font(cr, size=14, bold=True, color=WHITE)

        box = slide.shapes.add_textbox(Inches(1.25), Inches(y - 0.02), Inches(8.1), Inches(0.55))
        btf = box.text_frame
        bp = btf.paragraphs[0]
        br = bp.add_run()
        br.text = text
        set_run_font(br, size=15, color=SLATE)
        y += 0.82
    add_footer(slide)


def slide_governance_ask(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Governance Decision & KPIs")
    add_bullets(
        slide,
        [
            "Decision sought: Endorse Solvent Integrity Program for Exxsol D40 (policy + testing budget + audit schedule).",
            "Accountability: Procurement (sourcing), Quality (CoA & testing), EHS (SDS/flash point), Operations (dispensing traceability).",
            "Proposed KPIs:",
            ("100% of D40 lots received with verified CoA before release to production.", 1),
            ("Zero unauthorized suppliers on approved vendor list.", 1),
            ("≥1 independent GC-MS verification per quarter (or per new supplier).", 1),
            ("Mean time to quarantine suspect material < 4 hours of detection.", 1),
            ("Annual distributor audit closure rate 100%.", 1),
        ],
        top=1.45,
        size=15,
    )
    add_callout(
        slide,
        "The cost of prevention is a fraction of the cost of a single fire incident, mass scrap event, or customer stop-ship.",
        0.65,
        6.05,
        8.7,
        0.65,
        fill=RGBColor(0xDC, 0xFC, 0xE7),
        border=GREEN,
    )
    add_footer(slide)


def slide_appendix(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Appendix — Reference Contacts & Further Reading")
    add_bullets(
        slide,
        [
            "ExxonMobil product data: consult current Exxsol D40 Technical Data Sheet and SDS before use.",
            "Authorized distributors (verify current status with ExxonMobil):",
            ("Shanghai Huishuo — East/North China (est. 2003)", 1),
            ("Sang Hing Hong Group — South China & regional branches", 1),
            ("Additional regional suppliers — require authorization confirmation", 1),
            "Validation: run small-scale cleaning trials (time, temperature, agitation) for specific PM parts and contaminants.",
            "Regulatory: ensure compliance with local chemical storage, flammability, and occupational exposure regulations.",
            "Internal cross-reference: align with PPAP Element 10 (material/test results) and supplier quality requirements.",
        ],
        top=1.4,
        size=13,
    )
    add_footer(slide, "Appendix — Confidential")


def slide_thank_you(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(7.5)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()

    box = slide.shapes.add_textbox(Inches(1), Inches(2.8), Inches(8), Inches(1.5))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Questions & Discussion"
    set_run_font(run, size=36, bold=True, color=WHITE)

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    run2 = p2.add_run()
    run2.text = "Risk Committee — Exxsol D40 Supply Chain Integrity"
    set_run_font(run2, size=18, color=RGBColor(0xCB, 0xE5, 0xF0))


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    slide_title(prs)
    slide_executive_summary(prs)
    slide_agenda(prs)
    slide_business_context(prs)
    slide_product_profile(prs)
    slide_boiling_range(prs)
    slide_aromatic_content(prs)
    slide_d40_vs_d60(prs)
    slide_supply_risk(prs)
    slide_adulteration_threat(prs)
    slide_impact_table(prs)
    slide_operational_risks(prs)
    slide_distributor_controls(prs)
    slide_traceability(prs)
    slide_detection(prs)
    slide_recommendations(prs)
    slide_governance_ask(prs)
    slide_appendix(prs)
    slide_thank_you(prs)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    print(f"Saved: {OUTPUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_presentation()
