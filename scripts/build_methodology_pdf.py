"""Build the filing-ready CCAF release summary from repository artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
DASH = OUTPUT / "dashboards"
PDF_PATH = ROOT / "docs" / "CCAF_Framework_Methodology.pdf"
METHODOLOGY_PATH = ROOT / "docs" / "methodology.md"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPOSITORY_URL = "https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework"
VERSION_TAG_URL = f"{REPOSITORY_URL}/tree/v{VERSION}"

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#176B68")
BLUE = colors.HexColor("#376A91")
GREEN = colors.HexColor("#5F8D4E")
ORANGE = colors.HexColor("#B36B32")
LIGHT = colors.HexColor("#F2F5F7")
MID = colors.HexColor("#D7E0E7")
TEXT = colors.HexColor("#26333D")
MUTED = colors.HexColor("#5C6B76")


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=21, leading=24, textColor=NAVY, alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, textColor=MUTED, alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "Heading1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=13.5, leading=16, textColor=NAVY, spaceBefore=2, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "Heading2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=10.2, leading=12, textColor=TEAL, spaceBefore=5, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.4, leading=11.1, textColor=TEXT, spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.3, leading=9.2, textColor=TEXT, spaceAfter=2,
        ),
        "tiny": ParagraphStyle(
            "Tiny", parent=base["BodyText"], fontName="Helvetica",
            fontSize=6.6, leading=8.0, textColor=TEXT,
        ),
        "box": ParagraphStyle(
            "Box", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.7, leading=11.5, textColor=TEXT,
        ),
        "center": ParagraphStyle(
            "Center", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8, leading=10, textColor=TEXT, alignment=TA_CENTER,
        ),
    }


S = styles()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullet(text: str) -> Paragraph:
    return Paragraph(f"- {text}", S["body"])


def styled_table(data, widths, header=True, font_size=7.1, row_backgrounds=False):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, MID),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    if row_backgrounds:
        start = 1 if header else 0
        for row in range(start, len(data)):
            if (row - start) % 2:
                commands.append(("BACKGROUND", (0, row), (-1, row), LIGHT))
    table.setStyle(TableStyle(commands))
    return table


def page_header_footer(canvas, document) -> None:
    canvas.saveState()
    width, height = letter
    if document.page > 1:
        canvas.setStrokeColor(MID)
        canvas.line(0.68 * inch, height - 0.46 * inch, width - 0.68 * inch, height - 0.46 * inch)
    canvas.setStrokeColor(MID)
    canvas.line(0.68 * inch, 0.42 * inch, width - 0.68 * inch, 0.42 * inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.68 * inch, 0.27 * inch, "Synthetic demonstration - no institutional adoption or agency endorsement claimed")
    canvas.drawRightString(width - 0.68 * inch, 0.27 * inch, f"Page {document.page}")
    canvas.restoreState()


class MethodologyDocTemplate(SimpleDocTemplate):
    def afterPage(self) -> None:
        page_header_footer(self.canv, self)


def image(path: Path, width: float, height: float) -> Image:
    item = Image(str(path), width=width, height=height)
    item.hAlign = "CENTER"
    return item


def section_page(title: str) -> list:
    return [
        PageBreak(),
        p(title, "h1"),
    ]


def build() -> Path:
    modules = pd.read_csv(OUTPUT / "module_summary.csv")
    validation = pd.read_csv(OUTPUT / "seeded_validation_summary.csv")
    manifest = pd.read_csv(OUTPUT / "input_manifest.csv")
    source_assurance = pd.read_csv(OUTPUT / "source_assurance_record.csv")
    control_count = int(validation.control_id.nunique())
    total_seeded = int(validation.seeded_conditions.sum())
    total_detected = int(validation.seeded_conditions_detected.sum())
    total_exceptions = int(modules.exceptions.sum())
    methodology_sha256 = hashlib.sha256(METHODOLOGY_PATH.read_bytes()).hexdigest()

    document = MethodologyDocTemplate(
        str(PDF_PATH), pagesize=letter,
        rightMargin=0.68 * inch, leftMargin=0.68 * inch,
        topMargin=0.58 * inch, bottomMargin=0.55 * inch,
        title="CCAF - Continuous Control Assurance Framework",
        author="Ayodele Timothy Adeniyi",
        subject="Synthetic continuous-control analytics methodology",
    )
    story = []

    # Page 1: purpose and boundaries
    story.extend([
        Spacer(1, 0.25 * inch),
        p("Continuous Control Assurance Framework (CCAF)", "title"),
        p("A Nonproprietary Synthetic Demonstration for Financial and Digital-Payment Environments", "subtitle"),
        p(f"Ayodele Timothy Adeniyi, CISA, ACA<br/>Version {VERSION} | July 16, 2026 | Apache License 2.0", "center"),
        Spacer(1, 0.12 * inch),
    ])
    summary = Table([[p(
        "<b>Purpose.</b> CCAF is a vendor-neutral reference implementation that converts selected access, change-management, logging, reconciliation, and payment-monitoring objectives into repeatable control tests. It evaluates supplied in-scope records, identifies conditions for review, reports explicit evaluation status and eligible populations, and preserves artifacts needed to reproduce a run. This PDF summarizes the release; the detailed methodology and work-program procedures remain in the repository.",
        "box",
    )]], colWidths=[7.0 * inch])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.extend([summary, Spacer(1, 10), p("What the package contains", "h1")])
    contents = [
        [p("Working analytics", "small"), p("Twenty versioned control tests across privileged access, change/logging, and reconciliation/payment modules.", "small")],
        [p("Reproducible evidence", "small"), p("Synthetic data with planted conditions, source-assurance record, SHA-256 manifest, run metadata, calibration record, and regression tests.", "small")],
        [p("Transfer materials", "small"), p("Control-test catalog, configurable thresholds, reference SQL, implementation checklist, governance guidance, and framework traceability with interpretive boundaries.", "small")],
    ]
    story.append(styled_table(contents, [1.45 * inch, 5.55 * inch], header=False, font_size=7.4, row_backgrounds=True))
    story.extend([Spacer(1, 8), p("Evidence boundaries", "h1")])
    for text in [
        "The repository contains seeded synthetic data and independently written documentation and code; it contains no source workbook, employer template, client record, or production material.",
        "Full-population means every row in the supplied in-scope extract for the covered test. It does not prove source-system completeness or eliminate other audit risk.",
        "Detection of planted synthetic conditions is regression evidence for this fixed scenario, not a production accuracy rate or proof of loss reduction.",
        "Review-priority labels and scores order follow-up; they are not confirmed deficiencies, probabilities of breach, regulatory ratings, or calibrated financial-loss estimates.",
        "Framework mappings are traceability aids. No referenced organization has reviewed or endorsed CCAF.",
        "The 20 control tests are a bounded reference set selected for relevance, structured-data testability, transferability, analytical variety, and reproducible synthetic verification; they are not a comprehensive control catalog.",
        "CCAF complements enterprise IAM, SIEM, ITSM, GRC, ERP, fraud, payment-monitoring, and audit platforms. This release runs on demand; live connectors, scheduling, real-time monitoring, and remediation workflow require institution-authorized implementation.",
        f"Version {VERSION} is a maintenance release prepared on July 16, 2026, superseding version 1.3.0; no institutional adoption, agency endorsement, or external validation is claimed.",
    ]:
        story.append(bullet(text))
    story.append(Spacer(1, 8))
    status = Table([[
        f"{control_count}", f"{len(manifest):,}",
        f"{int(modules.eligible_control_evaluations.sum()):,}",
        f"{total_exceptions:,}",
    ], [
        p("control tests", "tiny"), p("source datasets<br/>(SHA-256 manifest)", "tiny"),
        p("eligible control evaluations", "tiny"), p("reported exceptions", "tiny"),
    ]], colWidths=[1.75 * inch] * 4)
    status.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 14),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.4, MID),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(status)

    # Page 2: controls and architecture
    story.extend(section_page("1. Architecture and Control Coverage"))
    architecture = [
        ["1. Validate", "2. Evaluate", "3. Report", "4. Preserve"],
        [p("Schemas, keys, timestamps, and selected relationships", "tiny"),
         p("Rule-based tests and peer-comparison screens", "tiny"),
         p("Structured exception records and per-control eligible populations", "tiny"),
         p("Hashes, configuration, calibration status, and run metadata", "tiny")],
    ]
    story.append(styled_table(architecture, [1.75 * inch] * 4, header=True, font_size=6.8))
    story.extend([Spacer(1, 8), p(
        "Blocking Critical or High source-data findings stop execution. Each test reports Completed or Not Evaluable, the population actually eligible for the procedure, and any resulting exceptions. A Not Evaluable test cannot appear as a clean result, and the framework does not assign synthetic module risk tiers.",
    )])
    controls_data = [["ID", "Control test", "Eligible population", "Review priority"]]
    controls = [
        ("PA-01", "Terminated user retains active privileged access", "Terminated users with active privileged grants", "Critical"),
        ("PA-02", "Privileged grant lacks approver", "Active privileged grants", "High"),
        ("PA-03", "Self-approved access grant", "Active grants", "High"),
        ("PA-04", "Dormant privileged account", "Active privileged users (extract must cover the dormancy period)", "Medium"),
        ("PA-05", "Toxic entitlement pair", "Users with active grants", "Critical"),
        ("PA-06", "After-hours authentication outlier", "Users meeting peer-comparison preconditions", "Medium"),
        ("PA-07", "Expired temporary privileged access", "Active temporary privileged grants", "Critical"),
        ("CM-01", "Implemented change lacks approval", "Implemented changes", "High"),
        ("CM-02", "Approver also implements change", "Implemented changes", "High"),
        ("CM-03", "Emergency change lacks review", "Emergency changes", "Medium"),
        ("CM-04", "Deployment lacks valid change record", "Deployment events", "Critical"),
        ("CM-05", "Log source exceeds heartbeat", "Log sources", "High"),
        ("CM-06", "Emergency-change rate spike", "Portfolio comparison", "Medium"),
        ("CM-07", "Implemented change lacks test evidence", "Implemented changes", "High"),
        ("TR-01", "Ledger item lacks processor match", "Ledger records past the settlement grace period", "High"),
        ("TR-02", "Ledger/processor amount difference", "Matched records", "High"),
        ("TR-03", "Duplicate transaction identifier", "Unique transaction IDs", "Critical"),
        ("TR-04", "Aged unreconciled item", "Unreconciled ledger records", "Medium"),
        ("TR-05", "Transaction-velocity outlier", "Accounts meeting peer-comparison preconditions", "Medium"),
        ("TR-06", "Threshold hovering below approval limit", "Accounts in ledger", "High"),
    ]
    controls_data.extend([
        [p(control_id, "tiny"), p(name, "tiny"), p(population, "tiny"), p(priority, "tiny")]
        for control_id, name, population, priority in controls
    ])
    story.append(styled_table(
        controls_data, [0.48 * inch, 3.12 * inch, 2.35 * inch, 1.05 * inch],
        header=True, font_size=6.35, row_backgrounds=True,
    ))
    story.extend([Spacer(1, 8), p("Detection and interpretation", "h2")])
    story.append(p(
        "Rule-based tests identify records that meet a defined review condition. Peer-comparison screens compare a user or account with the relevant population and flag observations far outside the typical range; the technical implementation uses a robust z-score based on the median and median absolute deviation so a small number of extreme values do not distort the baseline. Every exception is a lead for investigation, not a confirmed control deviation, deficiency, intent, or culpability. Bundled thresholds are demonstration defaults stored in <font name='Courier'>config/defaults.json</font>.",
    ))

    # Page 3: validation and transparent rates
    story.extend(section_page("2. Validation and Transparent Reporting"))
    story.append(p(
        f"The generator plants and labels {total_seeded} known test conditions. Automated regression tests detected {total_detected} of {total_seeded} planted conditions across all {control_count} control tests in this fixed synthetic scenario. The run also reported {int(validation.additional_synthetic_exceptions.sum())} additional peer-comparison observations. Because ordinary synthetic background records can satisfy a comparison rule, those observations require review and are not automatically classified as errors or false positives.",
    ))
    validation_table = [["Module", "Planted", "Detected", "Detected %", "Additional observations"]]
    for prefix, label in [("PA", "Privileged Access"), ("CM", "Change and Logging"), ("TR", "Reconciliation and Payments")]:
        subset = validation[validation.control_id.str.startswith(prefix)]
        validation_table.append([
            label,
            int(subset.seeded_conditions.sum()),
            int(subset.seeded_conditions_detected.sum()),
            f"{100 * subset.seeded_conditions_detected.sum() / subset.seeded_conditions.sum():.0f}%",
            int(subset.additional_synthetic_exceptions.sum()),
        ])
    story.append(styled_table(
        validation_table, [2.25 * inch, 1.0 * inch, 1.0 * inch, 0.9 * inch, 1.85 * inch],
        header=True, font_size=7.2, row_backgrounds=True,
    ))
    story.extend([Spacer(1, 7), p("Population reporting", "h2")])
    story.append(p(
        "Each test reports exceptions per 1,000 eligible records or entities. Module summaries add the eligible populations of only Completed tests and report exceptions per 1,000 eligible evaluations. These rates provide review context; they are not incident rates, error rates, or institution-level risk ratings.",
    ))
    module_table = [["Module", "Total", "Completed", "Not eval.", "Evaluations", "Exceptions", "Per 1,000"]]
    for row in modules.itertuples():
        module_table.append([
            row.module, row.tests_total, row.tests_completed, row.tests_not_evaluable,
            f"{row.eligible_control_evaluations:,}", row.exceptions,
            f"{row.exceptions_per_1000_evaluations:.2f}",
        ])
    story.append(styled_table(
        module_table, [2.05 * inch, 0.48 * inch, 0.62 * inch, 0.62 * inch, 1.08 * inch, 0.78 * inch, 0.88 * inch],
        header=True, font_size=6.7, row_backgrounds=True,
    ))
    story.extend([Spacer(1, 8), p("Demonstration outputs", "h2")])
    figures = Table([[
        image(DASH / "01_exceptions_by_control.png", 3.42 * inch, 2.35 * inch),
        image(DASH / "02_module_exception_rate.png", 3.42 * inch, 1.92 * inch),
    ], [
        p("Figure 1. Exceptions by control and review priority.", "tiny"),
        p("Figure 2. Exceptions per 1,000 eligible control evaluations.", "tiny"),
    ]], colWidths=[3.5 * inch, 3.5 * inch])
    figures.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(figures)
    story.extend([Spacer(1, 5), p("Review-priority score", "h2")])
    story.append(p(
        "Review-priority score = configurable review-priority weight x exposure factor (1.0-2.0). It orders follow-up work within the demonstration. It is not a loss probability, compliance rating, confirmed deficiency, or empirically calibrated risk score.",
    ))

    # Page 4: adoption and traceability
    story.extend(section_page("3. Implementation, Governance, and Traceability"))
    figures_2 = Table([[
        image(DASH / "03_review_priority_by_module.png", 3.42 * inch, 1.95 * inch),
        image(DASH / "04_reconciliation_aging.png", 3.42 * inch, 1.95 * inch),
    ], [
        p("Figure 3. Review-priority mix by module.", "tiny"),
        p("Figure 4. Weekday aging; production requires an approved holiday calendar.", "tiny"),
    ]], colWidths=[3.5 * inch, 3.5 * inch])
    figures_2.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(figures_2)
    story.extend([Spacer(1, 5), p("Control-assurance lifecycle", "h2")])
    story.append(p(
        "A production conclusion requires more than exception analytics. Teams document control scope and design, configuration and implementation, whether source records are complete and accurate for the procedure, operation across the period, exception disposition, and whether later changes could affect consistent operation since testing.",
    ))
    story.extend([Spacer(1, 6), p("Phased implementation", "h2")])
    phases = [
        ["Phase", "Required work"],
        ["0 - Authorize", "Approve scope, data access, schemas, thresholds, calendars, review-priority definitions, and escalation."],
        ["1 - Pilot", "Inspect authorized historical records, inquire regarding each exception, determine its disposition, assess reviewer effort, and calibrate."],
        ["2 - Operationalize", "Schedule authorized runs, integrate ticketing/GRC, apply retention and access controls, and monitor drift."],
        ["3 - Govern", "Obtain required approvals, train a second operator, revalidate after changes, and contribute only nonconfidential improvements."],
    ]
    story.append(styled_table(phases, [1.25 * inch, 5.75 * inch], header=True, font_size=7.1, row_backgrounds=True))
    story.extend([Spacer(1, 6), p("Framework traceability", "h2")])
    mapping = [
        ["Module", "Primary relevance", "Interpretive boundary"],
        [p("Privileged Access", "tiny"),
         p("NIST CSF PR.AA/GV.RR; FFIEC access administration; PCI DSS 7/8/10", "tiny"),
         p("Supports evidence organization; does not establish compliance.", "tiny")],
        [p("Change and Logging", "tiny"),
         p("NIST CSF PR.PS/DE.CM/DE.AE; FFIEC development and operations; PCI DSS 6/10", "tiny"),
         p("Test outputs require institutional scope and adjudication.", "tiny")],
        [p("Reconciliation and Payments", "tiny"),
         p("FFIEC payment-system reconciliation and integrity topics; supporting NIST detection relationships", "tiny"),
         p("NIST/PCI entries are supporting relationships, not direct reconciliation requirements.", "tiny")],
    ]
    story.append(styled_table(mapping, [1.55 * inch, 3.0 * inch, 2.45 * inch], header=True, font_size=6.9, row_backgrounds=True))
    story.extend([Spacer(1, 6), p("Governance artifacts", "h2")])
    story.append(p(
        f"A successful run creates the input hash manifest, source-assurance record, data-quality report, structured exception records, per-test evaluation summaries, calibration record, run metadata, and planted-condition verification summary. The demonstration leaves independent row-count and control-total reconciliation unresolved for all {len(source_assurance)} datasets. Adopting institutions must complete those fields, define retention and remediation requirements, and preserve exception dispositions.",
    ))

    # Page 5: limitations, references, and release status
    story.extend(section_page("4. Limitations, References, and Release Status"))
    story.append(p("Limitations", "h2"))
    for text in [
        "Synthetic verification demonstrates software behavior only for the fixed planted scenario; it does not establish production accuracy, adoption, or loss reduction.",
        "Source-extract completeness, field mapping, privacy, holiday calendars, expected activity, and thresholds must be validated locally; file hashes alone do not establish completeness.",
        "The framework is not a complete cybersecurity, fraud, anti-money-laundering, audit, or compliance program.",
        "Reference SQL uses database-dependent boolean, interval, and timestamp patterns and must be adapted and tested on the target platform.",
        "No agency, standards body, employer, client, examiner, or independent reviewer is represented as endorsing this version.",
    ]:
        story.append(bullet(text))

    story.extend([Spacer(1, 5), p("Authoritative references", "h2")])
    references = [
        "NIST, <b>The Cybersecurity Framework (CSF) 2.0</b>, NIST CSWP 29 (2024), https://doi.org/10.6028/NIST.CSWP.29.",
        "NIST, <b>Information Security Continuous Monitoring</b>, SP 800-137 (2011), https://doi.org/10.6028/NIST.SP.800-137.",
        "FFIEC, <b>Cybersecurity Assessment Tool Sunset</b>, https://www.ffiec.gov/cyberassessmenttool.htm. FFIEC states that it does not endorse a particular replacement tool.",
        "FFIEC, <b>Information Technology Examination Handbook InfoBase</b>, https://ithandbook.ffiec.gov/.",
        "PCI Security Standards Council, <b>PCI DSS v4.x</b>, https://www.pcisecuritystandards.org/standards/pci-dss/.",
        "U.S. Securities and Exchange Commission, rules implementing Sarbanes-Oxley Act Section 404 internal-control reporting requirements.",
        "The Institute of Internal Auditors, <b>GTAG: Continuous Auditing and Monitoring, 3rd Edition</b> (2025), https://www.theiia.org/en/content/guidance/recommended/supplemental/gtags/continuous-auditing-and-monitoring.",
    ]
    for number, reference in enumerate(references, start=1):
        story.append(p(f"{number}. {reference}", "small"))

    story.extend([Spacer(1, 5), p("Repository package", "h2")])
    story.append(p(
        "The package includes source code, planted-condition data and labels, JSON configuration, a source-metadata template, automated tests, reference SQL, source-assurance and run artifacts, generated exceptions and summaries, dashboards, a 20-test practitioner catalog, governance and implementation documents, Apache-2.0 license, changelog, version file, and citation metadata. This release summary is reproducible from <font name='Courier'>scripts/build_methodology_pdf.py</font>; the detailed method is documented in <font name='Courier'>docs/methodology.md</font>.",
    ))

    release = Table([[p(
        f"<b>Release status:</b> Version {VERSION} is a maintenance release prepared on July 16, 2026, superseding version 1.3.0. "
        f"Repository: {REPOSITORY_URL}. Version tag: {VERSION_TAG_URL}. "
        f"SHA-256 of <font name='Courier'>docs/methodology.md</font>: <font name='Courier' size='6'>{methodology_sha256}</font>. "
        "No institutional adoption, agency endorsement, or external validation is claimed.",
        "box",
    )]], colWidths=[7.0 * inch])
    release.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF6E8")),
        ("BOX", (0, 0), (-1, -1), 0.8, ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([Spacer(1, 6), release])

    document.build(story)
    return PDF_PATH


if __name__ == "__main__":
    print(build())
