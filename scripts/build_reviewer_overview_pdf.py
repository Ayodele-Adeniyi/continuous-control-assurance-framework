"""Build the two-page CCAF reviewer overview PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "CCAF_Reviewer_Overview.pdf"

NAVY = colors.HexColor("#193A5A")
TEAL = colors.HexColor("#16726F")
LIGHT_BLUE = colors.HexColor("#EAF0F5")
LIGHT_TEAL = colors.HexColor("#E8F3F1")
GRID = colors.HexColor("#9BACBA")
TEXT = colors.HexColor("#1C2731")
MUTED = colors.HexColor("#53616D")


CONTROL_ROWS = [
    ("PA-01", "Active privileged access after termination", "Terminated user retains an active privileged grant"),
    ("PA-02", "Recorded approval before access activation", "Active grant has no recorded approver"),
    ("PA-03", "Separation of grantee and approver", "User approved the user's own access"),
    ("PA-04", "Dormant privileged access", "No successful authentication within the approved dormancy period"),
    ("PA-05", "Incompatible entitlements", "User holds an institution-defined conflicting entitlement pair"),
    ("PA-06", "Unusual after-hours privileged activity", "Activity exceeds the approved peer-comparison threshold"),
    ("PA-07", "Expired temporary privileged access", "Grant remains active after approved expiry and grace period"),
    ("CM-01", "Approval for implemented production changes", "Implemented change lacks recorded approval"),
    ("CM-02", "Separation of approval and implementation", "Same identifier approved and implemented a change"),
    ("CM-03", "Review of emergency changes", "Emergency change lacks post-implementation review"),
    ("CM-04", "Deployment linked to a valid change", "Production deployment lacks a valid change reference"),
    ("CM-05", "Timely reporting by required log sources", "Source exceeds the approved heartbeat interval"),
    ("CM-06", "Emergency-change rate against baseline", "Recent rate meets the configured increase threshold"),
    ("CM-07", "Preproduction testing and approval", "Change lacks testing or test-approval evidence"),
    ("TR-01", "Ledger-to-processor settlement matching", "Due ledger item lacks a processor-settlement record"),
    ("TR-02", "Amount consistency within tolerance", "Matched amounts differ beyond approved tolerance"),
    ("TR-03", "Transaction-identifier uniqueness", "Identifier appears in more than one ledger row"),
    ("TR-04", "Aging of unreconciled items", "Open item exceeds the approved aging period"),
    ("TR-05", "Unusual transaction velocity", "Activity exceeds the approved peer-comparison threshold"),
    ("TR-06", "Activity below an approval limit", "Account meets the configured threshold-hovering pattern"),
]


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=20,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.2,
            leading=12,
            textColor=TEAL,
            spaceBefore=5,
            spaceAfter=2,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.25,
            leading=10.3,
            textColor=TEXT,
            spaceAfter=3,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.25,
            leading=8.6,
            textColor=TEXT,
        ),
        "tiny": ParagraphStyle(
            "Tiny",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=6.55,
            leading=7.55,
            textColor=TEXT,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=7.8,
            textColor=colors.white,
        ),
        "note": ParagraphStyle(
            "Note",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.6,
            leading=9.2,
            textColor=TEXT,
            leftIndent=4,
            rightIndent=4,
        ),
    }


def p(text: str, style):
    return Paragraph(text, style)


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#C7D2DB"))
    canvas.setLineWidth(0.5)
    left = 0.48 * inch
    right = letter[0] - 0.48 * inch
    canvas.line(left, 0.43 * inch, right, 0.43 * inch)
    canvas.setFont("Helvetica", 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(left, 0.25 * inch, "CCAF Version 1.3.1 | Synthetic Reference Prototype")
    canvas.drawRightString(right, 0.25 * inch, f"Reviewer Overview | {doc.page}")
    canvas.restoreState()


def build() -> Path:
    st = styles()
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.48 * inch,
        rightMargin=0.48 * inch,
        topMargin=0.38 * inch,
        bottomMargin=0.52 * inch,
        title="CCAF Reviewer Overview",
        author="Ayodele Timothy Adeniyi",
        subject="Plain-language reviewer overview and 20-test quick reference",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(id="overview", frames=frame, onPageEnd=page_footer))

    story = []
    story.append(p("CCAF Reviewer Overview", st["title"]))
    story.append(p("Version 1.3.1 | Synthetic Reference Prototype | Stable snapshot: review-v1.3.1", st["subtitle"]))

    story.append(p("What CCAF is", st["h2"]))
    story.append(
        p(
            "The <b>Continuous Control Assurance Framework (CCAF)</b> is a documented methodology and open-source reference implementation for applying repeatable analytics to authorized data extracts. It helps audit, risk, and cybersecurity teams expand beyond periodic sampling by testing every eligible record in the supplied in-scope extract and organizing reported conditions for professional follow-up.",
            st["body"],
        )
    )
    story.append(
        p(
            "CCAF does not establish that a source extract is complete, determine control effectiveness, or make remediation decisions. It applies transparent procedures consistently and preserves the evidence needed to understand and reproduce the run.",
            st["body"],
        )
    )

    story.append(p("How it works", st["h2"]))
    flow = Table(
        [[p("Authorized extracts", st["small"]), ">", p("Source checks", st["small"]), ">", p("20 procedures", st["small"]), ">", p("Exceptions + evidence", st["small"]), ">", p("Professional review", st["small"])]],
        colWidths=[1.12 * inch, 0.18 * inch, 0.95 * inch, 0.18 * inch, 0.88 * inch, 0.18 * inch, 1.38 * inch, 0.18 * inch, 1.18 * inch],
    )
    flow.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_TEAL),
                ("TEXTCOLOR", (1, 0), (1, 0), TEAL),
                ("TEXTCOLOR", (3, 0), (3, 0), TEAL),
                ("TEXTCOLOR", (5, 0), (5, 0), TEAL),
                ("TEXTCOLOR", (7, 0), (7, 0), TEAL),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.5, GRID),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(flow)

    story.append(p("What it tests", st["h2"]))
    module_data = [
        [p("Module", st["table_header"]), p("Tests", st["table_header"]), p("Focus", st["table_header"]), p("Example condition reported for review", st["table_header"])],
        [p("Privileged Access", st["small"]), "7", p("Access status, approval, conflicts, dormancy, activity, and expiry", st["small"]), p("Terminated user retains active privileged access", st["small"])],
        [p("Change Management and Logging", st["small"]), "7", p("Approval, separation, emergency review, deployment, logs, and testing", st["small"]), p("Production deployment lacks a valid change record", st["small"])],
        [p("Reconciliation and Payments", st["small"]), "6", p("Settlement, tolerance, identifiers, aging, activity, and threshold patterns", st["small"]), p("Due ledger item lacks a processor-settlement record", st["small"])],
    ]
    modules = Table(module_data, colWidths=[1.35 * inch, 0.42 * inch, 2.75 * inch, 2.55 * inch], repeatRows=1)
    modules.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(modules)

    story.append(p("What the fixed demonstration establishes", st["h2"]))
    benchmark_data = [
        [p("Module", st["table_header"]), p("Planted", st["table_header"]), p("Reported", st["table_header"])],
        ["Privileged Access", "39", "39"],
        ["Change Management and Logging", "49", "49"],
        ["Reconciliation and Payments", "77", "77"],
        [p("Total", st["small"]), p("165", st["small"]), p("165", st["small"])],
    ]
    benchmark = Table(benchmark_data, colWidths=[3.55 * inch, 1.0 * inch, 1.0 * inch], repeatRows=1, hAlign="LEFT")
    benchmark.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, -1), (-1, -1), LIGHT_TEAL),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.4),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    story.append(benchmark)
    story.append(
        p(
            "The official seed-42 run also reported <b>3 additional peer-comparison observations</b>, producing <b>168 total exceptions</b>. This is regression evidence for the fixed synthetic scenario, not a production detection rate, external validation, or evidence of adoption.",
            st["note"],
        )
    )

    story.append(p("Interpretation boundaries", st["h2"]))
    boundaries = [
        "Synthetic demonstration data only; no employer, client, or production information is included.",
        '"Every eligible record" refers only to the supplied in-scope extract, not an institution\'s unverified full population.',
        "A reported exception is a condition for investigation, not a confirmed control deviation or deficiency.",
        "The bounded 20-test reference set complements rather than replaces enterprise security, GRC, audit, or monitoring platforms.",
        "No institutional adoption, regulatory approval, certification, external validation, or production performance is claimed.",
    ]
    boundary_table = Table([[p("- " + item, st["small"])] for item in boundaries], colWidths=[7.05 * inch])
    boundary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.5, GRID),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    story.append(boundary_table)
    story.append(p("For the reviewer", st["h2"]))
    story.append(
        p(
            "A document-based design review of the methodology and control-test catalog is sufficient. Repository inspection and local reproduction are optional. The response should identify the materials and procedures personally examined and reflect the reviewer's independent professional judgment.",
            st["body"],
        )
    )

    story.append(PageBreak())
    story.append(p("CCAF Control-Test Quick Reference", st["title"]))
    story.append(p("20 detective procedures | Three modules | Version 1.3.1", st["subtitle"]))

    table_data = [[p("ID", st["table_header"]), p("Procedure focus", st["table_header"]), p("Example condition reported for review", st["table_header"])]]
    for control_id, focus, example in CONTROL_ROWS:
        table_data.append([p(control_id, st["tiny"]), p(focus, st["tiny"]), p(example, st["tiny"])])
    controls = Table(table_data, colWidths=[0.52 * inch, 2.65 * inch, 3.88 * inch], repeatRows=1)
    controls.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.3, GRID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2.2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
                ("LINEABOVE", (0, 8), (-1, 8), 1.0, TEAL),
                ("LINEABOVE", (0, 15), (-1, 15), 1.0, TEAL),
            ]
        )
    )
    story.append(controls)
    story.append(Spacer(1, 5))

    interpretation = [
        [p("Completed", st["small"]), p("Required records and analytical conditions were present; the result applies only to the reported eligible population.", st["small"])],
        [p("Not Evaluable", st["small"]), p("A required condition was absent; no clean result or exception rate is implied.", st["small"])],
        [p("Tailoring", st["small"]), p("Source mappings, thresholds, calendars, policies, peer groups, conflict matrices, roles, and escalation requirements must be authorized and validated locally.", st["small"])],
        [p("Evidence", st["small"]), p("Retain approved configuration, source queries or reports, source-assurance and data-quality records, status, eligible population, exceptions, rule version, input hashes, disposition, and supporting records.", st["small"])],
    ]
    interpretation_table = Table(interpretation, colWidths=[0.92 * inch, 6.13 * inch])
    interpretation_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_TEAL),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(interpretation_table)
    story.append(Spacer(1, 5))
    conclusion = Table(
        [[p("An automated exception begins professional investigation. It does not by itself establish a control deviation, deficiency, misconduct, compliance failure, or financial loss.", st["note"]) ]],
        colWidths=[7.05 * inch],
    )
    conclusion.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.5, GRID),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(conclusion)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    print(build())
