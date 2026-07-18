"""Build the reviewer-facing CCAF control-test catalog PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    CondPageBreak,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "control-test-catalog.md"
OUTPUT = ROOT / "docs" / "CCAF_Control_Test_Catalog.pdf"

NAVY = colors.HexColor("#193A5A")
BLUE = colors.HexColor("#2C6E91")
LIGHT_BLUE = colors.HexColor("#EAF0F5")
LIGHT_GRAY = colors.HexColor("#F3F5F7")
MID_GRAY = colors.HexColor("#60717F")
TEXT = colors.HexColor("#1C2731")
RULE = colors.HexColor("#B6C2CC")


def clean(value: str) -> str:
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2011", "-")
    value = re.sub(r"\*\*(.+?)\*\*", r"\1", value)
    value = re.sub(r"`(.+?)`", r"\1", value)
    return html.escape(value.strip())


def parse_catalog() -> list[dict[str, str]]:
    module = ""
    rows: list[dict[str, str]] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Module "):
            module = line.removeprefix("## ").strip()
            continue
        if not line.startswith(("| PA-", "| CM-", "| TR-")):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            raise ValueError(f"Unexpected control-catalog row: {line}")
        rows.append({
            "module": module,
            "control_id": cells[0],
            "risk": cells[1],
            "control_statement": cells[2],
            "procedure": cells[3],
            "test_type": cells[4],
            "follow_up": cells[5],
        })
    if len(rows) != 20:
        raise ValueError(f"Expected 20 controls, found {len(rows)}")
    return rows


def header_footer(canvas, document) -> None:
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(0.58 * inch, height - 0.42 * inch, width - 0.58 * inch, height - 0.42 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MID_GRAY)
    canvas.drawString(0.58 * inch, height - 0.32 * inch, "CCAF Control-Test Catalog | Version 1.3.1")
    canvas.drawRightString(width - 0.58 * inch, 0.30 * inch, f"Page {document.page}")
    canvas.restoreState()


def build() -> Path:
    controls = parse_catalog()
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "CatalogTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=5,
    )
    subtitle = ParagraphStyle(
        "CatalogSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=MID_GRAY,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    section = ParagraphStyle(
        "CatalogSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=5,
        keepWithNext=True,
    )
    control_heading = ParagraphStyle(
        "ControlHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.white,
        leftIndent=6,
        rightIndent=6,
        spaceBefore=0,
        spaceAfter=0,
    )
    body = ParagraphStyle(
        "CatalogBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.4,
        leading=11.1,
        textColor=TEXT,
        spaceAfter=3,
    )
    note = ParagraphStyle(
        "CatalogNote",
        parent=body,
        fontSize=8.2,
        leading=10.8,
        textColor=MID_GRAY,
    )
    label = ParagraphStyle(
        "CatalogLabel",
        parent=body,
        fontName="Helvetica-Bold",
        textColor=NAVY,
        spaceAfter=1,
        keepWithNext=True,
    )

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.58 * inch,
        leftMargin=0.58 * inch,
        topMargin=0.57 * inch,
        bottomMargin=0.48 * inch,
        title="CCAF Control-Test Catalog",
        author="Ayodele Timothy Adeniyi",
        subject="Reviewer-facing work program for CCAF Version 1.3.1",
    )

    story = [
        Spacer(1, 0.16 * inch),
        Paragraph("CCAF Control-Test Catalog", title),
        Paragraph(
            "Reviewer edition | Continuous Control Assurance Framework | Version 1.3.1",
            subtitle,
        ),
    ]

    orientation = Table(
        [[Paragraph(
            "<b>Purpose.</b> This catalog is the practitioner work program for the 20-test "
            "reference prototype. It allows a reviewer to assess the professional coherence "
            "of each risk, intended control state, automated procedure, and evidence follow-up "
            "without running the software.",
            body,
        )]],
        colWidths=[7.22 * inch],
    )
    orientation.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.7, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([
        orientation,
        Spacer(1, 8),
        Paragraph("Review boundaries", section),
        Paragraph(
            "All tests are detective automated inspection or reperformance procedures. A "
            "reported condition begins an investigation; it does not by itself establish a "
            "control deviation, deficiency, misconduct, compliance failure, or financial loss.",
            body,
        ),
        Paragraph(
            "Before relying on a completed test, an institution must establish that the "
            "queries, reports, filters, period, mappings, row counts, control totals, and "
            "approvals used to create each extract are complete and accurate for that procedure. "
            "File hashes preserve identity after extraction; they do not prove source completeness.",
            body,
        ),
        Paragraph(
            "Completed means the required records and analytical preconditions were present. "
            "Not Evaluable means a stated precondition was absent; no exception rate may be "
            "interpreted as a clean result. Bracketed language is an institution-specific "
            "tailoring point.",
            body,
        ),
        PageBreak(),
    ])

    current_module = ""
    for item in controls:
        if item["module"] != current_module:
            current_module = item["module"]
            story.append(Paragraph(clean(current_module), section))
        story.append(CondPageBreak(2.25 * inch))
        heading_table = Table(
            [[Paragraph(
                f"{clean(item['control_id'])} | {clean(item['test_type'])}",
                control_heading,
            )]],
            colWidths=[7.22 * inch],
        )
        heading_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([
            heading_table,
            Spacer(1, 4),
            Paragraph("Risk addressed", label),
            Paragraph(clean(item["risk"]), body),
            Paragraph("Intended control state", label),
            Paragraph(clean(item["control_statement"]), body),
            Paragraph("Automated procedure", label),
            Paragraph(clean(item["procedure"]), body),
            Paragraph("Evidence and professional follow-up", label),
            Paragraph(clean(item["follow_up"]), note),
            Spacer(1, 5),
        ])

    story.extend([
        CondPageBreak(2.0 * inch),
        Paragraph("Evidence and conclusion protocol", section),
        Paragraph(
            "For every completed test, teams retain the approved configuration, source queries "
            "or reports, source-assurance record, data-quality results, evaluation status, "
            "eligible population, exception records, rule version, input hashes, reviewer "
            "disposition, and supporting records.",
            body,
        ),
        Paragraph(
            "CCAF produces an automated exception and structures evidence for follow-up. An "
            "authorized reviewer must investigate the condition, determine whether a confirmed "
            "deviation exists, and evaluate any deficiency or finding under the institution's "
            "methodology. Those later judgments are not automated.",
            body,
        ),
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return OUTPUT


if __name__ == "__main__":
    print(build())
