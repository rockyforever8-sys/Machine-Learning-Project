#!/usr/bin/env python3
"""Generate C-suite Risk Committee presentation: Exxsol D40 supply chain integrity."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from generate_slide_graphics import ASSETS, generate_all

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

# Layout constants — content left, graphic right
IMG_LEFT = 6.35
IMG_TOP = 1.35
IMG_W = 3.35
IMG_H = 5.35
TEXT_LEFT = 0.45
TEXT_TOP = 1.35
TEXT_W = 5.65


def set_run_font(run, size=22, bold=False, color=SLATE, name="Calibri"):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_footer(slide, text="Confidential — Risk Committee | Exxsol D40"):
    box = slide.shapes.add_textbox(Inches(0.4), Inches(7.08), Inches(9.2), Inches(0.28))
    p = box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = text
    set_run_font(run, size=10, color=MID_GRAY)


def add_title_bar(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(1.2)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.45), Inches(0.18), Inches(9.1), Inches(0.62))
    run = title_box.text_frame.paragraphs[0].add_run()
    run.text = title
    set_run_font(run, size=34, bold=True, color=WHITE)

    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.45), Inches(0.72), Inches(9.1), Inches(0.38))
        srun = sub_box.text_frame.paragraphs[0].add_run()
        srun.text = subtitle
        set_run_font(srun, size=18, color=RGBColor(0xCB, 0xE5, 0xF0))


def add_slide_image(slide, asset_name: str):
    path = ASSETS / f"{asset_name}.png"
    if path.exists():
        slide.shapes.add_picture(str(path), Inches(IMG_LEFT), Inches(IMG_TOP), Inches(IMG_W), Inches(IMG_H))


def add_bullets(slide, items, left=TEXT_LEFT, top=TEXT_TOP, width=TEXT_W, size=24, max_items=4):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(5.6))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP

    for i, item in enumerate(items[:max_items]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        level = item[1] if isinstance(item, tuple) else 0
        text = item[0] if isinstance(item, tuple) else item
        p.level = level
        run = p.add_run()
        run.text = f"• {text}" if level == 0 else f"  – {text}"
        set_run_font(run, size=size - (4 if level else 0), color=SLATE)
        p.space_after = Pt(14)
        p.space_before = Pt(4)


def add_callout(slide, text, top=6.15, width=5.65, size=16):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(TEXT_LEFT),
        Inches(top),
        Inches(width),
        Inches(0.72),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xFE, 0xF3, 0xC7)
    shape.line.color.rgb = AMBER
    shape.line.width = Pt(1.5)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.12)
    tf.margin_right = Inches(0.12)
    run = tf.paragraphs[0].add_run()
    run.text = text
    set_run_font(run, size=size, bold=True, color=NAVY)


def add_compact_table(slide, headers, rows, col_widths, top=1.35, font_size=13):
    rows_n = len(rows) + 1
    cols_n = len(headers)
    table_shape = slide.shapes.add_table(
        rows_n, cols_n, Inches(TEXT_LEFT), Inches(top), Inches(5.65), Inches(0.38 * rows_n + 0.2)
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
            for run in p.runs:
                set_run_font(run, size=font_size, bold=True, color=WHITE)

    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_GRAY
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    set_run_font(run, size=font_size - 1, color=SLATE)


def slide_title(prs, asset="01_title"):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()

    add_slide_image(slide, asset)
    # Reposition hero image full-width overlay on right
    for shape in list(slide.shapes):
        if shape.shape_type == 13:  # picture
            slide.shapes._spTree.remove(shape._element)
    slide.shapes.add_picture(str(ASSETS / f"{asset}.png"), Inches(5.2), Inches(0), Inches(4.8), Inches(7.5))

    box = slide.shapes.add_textbox(Inches(0.6), Inches(1.6), Inches(4.6), Inches(4.5))
    tf = box.text_frame
    lines = [
        ("Exxsol D40\nSupply Chain Risk", 38, True, WHITE),
        ("Quality • Traceability • Anti-Adulteration", 20, False, RGBColor(0xCB, 0xE5, 0xF0)),
        ("Risk Committee Briefing", 18, False, RGBColor(0xE2, 0xE8, 0xF0)),
        ("Powder Metallurgy Cleaning", 16, False, RGBColor(0xE2, 0xE8, 0xF0)),
        ("September 2026", 16, False, RGBColor(0xE2, 0xE8, 0xF0)),
    ]
    for i, (text, sz, bold, col) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = text
        set_run_font(run, size=sz, bold=bold, color=col)
        p.space_after = Pt(10)


def content_slide(prs, title, bullets, asset, subtitle=None, callout=None, table=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, title, subtitle)
    add_slide_image(slide, asset)
    if table:
        headers, rows, widths = table
        add_compact_table(slide, headers, rows, widths)
    else:
        add_bullets(slide, bullets, size=24)
    if callout:
        add_callout(slide, callout)
    add_footer(slide)
    return slide


def slide_executive_summary(prs):
    content_slide(
        prs,
        "Executive Summary",
        [
            "D40 cleans porous PM parts before plating/coating",
            "Price pressure drives drum adulteration risk",
            "Fake fluid = fire, HSE & quality failures",
            "Defense: authorized supply + CoA + GC-MS",
        ],
        "02_executive",
        callout="Cheap drums cost more than they save.",
    )


def slide_agenda(prs):
    content_slide(
        prs,
        "Agenda",
        [
            "Why D40 specs matter",
            "Boiling range & aromatics",
            "Supply chain risk",
            "Controls & actions",
        ],
        "03_agenda",
    )


def slide_business_context(prs):
    content_slide(
        prs,
        "Business Context",
        [
            "PM pores trap oils — need residue-free clean",
            "D40: fast dry, low odor, metal-safe",
            "Not a commodity — specs are critical",
            "Look-alike solvents increase fraud risk",
        ],
        "04_business",
        subtitle="Why D40 Is on the Agenda",
    )


def slide_product_profile(prs):
    content_slide(
        prs,
        "Product Profile",
        [],
        "05_product",
        subtitle="Exxsol D40 Key Specs",
        table=(
            ["Spec", "Value", "Why It Matters"],
            [
                ["Distillation", "163–187 °C", "Uniform dry"],
                ["Flash point", "~48 °C", "Flammable"],
                ["Aromatics", "<0.1%", "Safe, clean"],
                ["OEL", "1200 mg/m³", "4× vs white spirit"],
            ],
            [1.3, 1.5, 2.85],
        ),
    )


def slide_boiling_range(prs):
    content_slide(
        prs,
        "Boiling Range",
        [
            "IBP = first drop; DP = last drop",
            "Narrow range = predictable drying",
            "Heavy ends stay in PM pores",
            "MC/methanol breaks the profile",
        ],
        "06_boiling",
        subtitle="IBP • Dry Point • Narrow Window",
        callout="Adulteration = residue in pores.",
    )


def slide_aromatic_content(prs):
    content_slide(
        prs,
        "Low Aromatics",
        [
            "Less odor & toxicity for workers",
            "Safe for seals & elastomers",
            "Clean surface for plating",
            "Adulteration voids certification",
        ],
        "07_aromatic",
        subtitle="Dearomatized = Engineered Safety",
    )


def slide_d40_vs_d60(prs):
    content_slide(
        prs,
        "D40 vs D60",
        [],
        "08_compare",
        table=(
            ["", "D40", "D60(S)"],
            [
                ["Boil range", "163–187 °C", "180–210 °C"],
                ["Flash point", "~48 °C", "~68 °C"],
                ["Dry speed", "Fast", "Slower"],
                ["Best for", "PM fast clean", "Higher flash needs"],
            ],
            [1.2, 2.2, 2.25],
        ),
    )


def slide_supply_risk(prs):
    content_slide(
        prs,
        "Supply Chain Risk",
        [
            "Middle East conflict → feedstock stress",
            "ExxonMobil +$0.06/lb (Mar 2026)",
            "China price +5% and rising",
            "Wide spread = fraud incentive",
        ],
        "09_supply",
        callout="Verify — don't buy on price alone.",
    )


def slide_adulteration_threat(prs):
    content_slide(
        prs,
        "Adulteration Threat",
        [
            "Traders mix MC & methanol to cut cost",
            "Reuse real drums & fake CoA",
            "Looks clear — hard to spot",
            "Illegal & invalidates SDS",
        ],
        "10_adulteration",
        subtitle="How Fraud Happens",
    )


def slide_impact_table(prs):
    content_slide(
        prs,
        "Impact of Fraud",
        [],
        "11_impact",
        table=(
            ["Property", "Genuine", "Adulterated"],
            [
                ["Distillation", "163–187 °C", "Starts ~40 °C"],
                ["Flash point", "~48 °C", "Much lower"],
                ["Cleaning", "Controlled", "Fails"],
                ["Downstream", "Clean surface", "Coating peel"],
            ],
            [1.5, 2.0, 2.15],
        ),
    )


def slide_operational_risks(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Enterprise Risk")
    add_slide_image(slide, "12_enterprise")
    risks = [
        ("Safety", "Fire & SDS breach", RED),
        ("Quality", "Plating & coating fail", AMBER),
        ("Operations", "Scrap & downtime", AMBER),
        ("Reputation", "Customer stop-ship", NAVY),
    ]
    y = 1.45
    for title, body, color in risks:
        shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(y), Inches(5.65), Inches(1.05)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = LIGHT_GRAY
        shape.line.color.rgb = color
        shape.line.width = Pt(3)
        tf = shape.text_frame
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{title}: "
        set_run_font(r1, size=22, bold=True, color=color)
        r2 = p.add_run()
        r2.text = body
        set_run_font(r2, size=20, color=SLATE)
        y += 1.2
    add_footer(slide)


def slide_distributor_controls(prs):
    content_slide(
        prs,
        "Distributor QC",
        [
            "Buy only authorized distributors",
            "Batch CoA before receipt",
            "Check IBP, flash, aromatics",
            "Inspect seals & drum labels",
        ],
        "13_qc",
        subtitle="Three Lines of Defense",
    )


def slide_traceability(prs):
    content_slide(
        prs,
        "Traceability",
        [
            "Track lot: maker → line → part",
            "Barcode drum to CoA in ERP",
            "Annual distributor audit",
            "Quarantine suspect lots fast",
        ],
        "14_trace",
        subtitle="Chain of Custody",
    )


def slide_detection(prs):
    content_slide(
        prs,
        "Detection Controls",
        [],
        "15_detection",
        table=(
            ["Control", "When", "Goal"],
            [
                ["CoA review", "Every batch", "Spec match"],
                ["On-site screen", "Each lot", "Quick flag"],
                ["GC-MS test", "Quarterly", "Prove purity"],
                ["Price check", "Ongoing", "Spot fraud"],
            ],
            [1.8, 1.5, 2.35],
        ),
    )


def slide_recommendations(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(slide, "Recommended Actions", "Approval Requested")
    add_slide_image(slide, "16_actions")
    actions = [
        "Authorized distributors only",
        "CoA + quarantine all receipts",
        "Fund quarterly GC-MS testing",
        "ERP drum-to-line traceability",
        "Distributor audit in 90 days",
    ]
    y = 1.5
    for i, text in enumerate(actions, 1):
        circle = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.OVAL, Inches(0.5), Inches(y), Inches(0.5), Inches(0.5)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = TEAL
        circle.line.fill.background()
        cp = circle.text_frame.paragraphs[0]
        cp.alignment = PP_ALIGN.CENTER
        cr = cp.add_run()
        cr.text = str(i)
        set_run_font(cr, size=18, bold=True, color=WHITE)

        box = slide.shapes.add_textbox(Inches(1.15), Inches(y + 0.05), Inches(4.9), Inches(0.5))
        br = box.text_frame.paragraphs[0].add_run()
        br.text = text
        set_run_font(br, size=22, color=SLATE)
        y += 0.95
    add_footer(slide)


def slide_governance_ask(prs):
    content_slide(
        prs,
        "Governance & KPIs",
        [
            "Approve Solvent Integrity Program",
            "100% CoA verified before use",
            "Zero unauthorized suppliers",
            "Quarterly GC-MS minimum",
        ],
        "17_governance",
        callout="Prevention costs less than one incident.",
    )


def slide_appendix(prs):
    content_slide(
        prs,
        "Appendix",
        [
            "Verify distributors with ExxonMobil",
            "Shanghai Huishuo — East/North China",
            "Sang Hing Hong — South China",
            "Align with PPAP Element 10",
        ],
        "18_appendix",
        subtitle="References",
    )


def slide_thank_you(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    slide.shapes.add_picture(str(ASSETS / "19_qa.png"), Inches(5.0), Inches(0.8), Inches(4.6), Inches(5.8))

    box = slide.shapes.add_textbox(Inches(0.7), Inches(2.5), Inches(4.2), Inches(2.5))
    tf = box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Questions?"
    set_run_font(run, size=44, bold=True, color=WHITE)
    p2 = tf.add_paragraph()
    run2 = p2.add_run()
    run2.text = "Risk Committee\nExxsol D40 Integrity"
    set_run_font(run2, size=22, color=RGBColor(0xCB, 0xE5, 0xF0))


def build_presentation():
    generate_all()
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

    prs.save(OUTPUT)
    print(f"Saved: {OUTPUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_presentation()
