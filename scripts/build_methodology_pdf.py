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
        "<b>Purpose.</b> CCAF addresses a practical assurance task: turning selected access, change-management, logging, reconciliation, and payment-monitoring objectives into repeatable tests over authorized records. It identifies conditions for review and preserves the population, configuration, exceptions, and run evidence needed for a reviewer to understand and reproduce the work.",
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
    story.extend([summary, Spacer(1, 10), p("How to read this summary", "h1")])
    roadmap = [
        [p("1. Run", "small"), p("How CCAF validates records, executes tests, reports results, and preserves evidence.", "small")],
        [p("2. Test", "small"), p("What the three modules examine and how rule-based and comparison procedures differ.", "small")],
        [p("3. Interpret", "small"), p("What the synthetic demonstration showed and what its counts, rates, and priorities mean.", "small")],
        [p("4. Adopt", "small"), p("What an institution must authorize, validate, investigate, and govern before operational use.", "small")],
    ]
    story.append(styled_table(roadmap, [1.0 * inch, 6.0 * inch], header=False, font_size=7.4, row_backgrounds=True))
    story.extend([Spacer(1, 8), p("Evidence boundaries", "h1")])
    for text in [
        "The repository contains seeded synthetic data and independently written documentation and code; no employer, client, or production material was used.",
        "All results describe the fixed synthetic demonstration: full-population means every row of the supplied in-scope extract, and detection of planted conditions is regression evidence, not a production accuracy rate.",
        "The 20 tests are a bounded reference set, not a comprehensive catalog, and complement rather than replace enterprise security, GRC, and audit platforms.",
        "No institutional adoption, external validation, or endorsement by any referenced organization is claimed.",
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

    # Page 2: the run from source records to preserved evidence
    story.extend(section_page("1. How a CCAF Run Works"))
    story.append(p(
        "A run follows a sequence that a reviewer can inspect and repeat: validate the supplied records, execute the approved tests, report the conditions identified, and preserve the evidence of what was performed.",
    ))
    architecture = [
        ["1. Validate", "2. Evaluate", "3. Report", "4. Preserve"],
        [p("Check schemas, keys, timestamps, values, and selected relationships.", "tiny"),
         p("Apply versioned rule-based tests and comparison procedures.", "tiny"),
         p("Record status, eligible population, exceptions, and review priority.", "tiny"),
         p("Retain hashes, configuration, calibration, and run metadata.", "tiny")],
    ]
    story.append(styled_table(architecture, [1.75 * inch] * 4, header=True, font_size=6.8))

    story.extend([Spacer(1, 9), p("Why validation comes first", "h2")])
    story.append(p(
        "Every result depends on the supplied records. A Critical or High data-quality finding stops the run before any control test executes. Prior outputs are cleared at the start of the run so an unsuccessful execution cannot leave stale exception files that appear current.",
    ))
    source_rows = [
        ["Framework checks", "Practitioner evidence still required"],
        [p("Required files and fields; empty extracts; key completeness and uniqueness; timestamps; selected values and relationships.", "small"),
         p("Queries or reports used to generate the extracts; filters and period coverage; expected counts or totals; owner review and reconciliation.", "small")],
    ]
    story.append(styled_table(source_rows, [3.5 * inch, 3.5 * inch], header=True, font_size=7.0))
    story.append(p(
        "The resulting source-assurance record declares what was supplied and what remains unresolved. File hashes preserve file identity after extraction; they do not establish that the extraction was complete or correctly scoped.",
    ))

    story.extend([Spacer(1, 7), p("Two possible test outcomes", "h2")])
    status_rows = [
        ["Status", "Meaning", "How it is reported"],
        [p("Completed", "small"), p("The required records and analytical conditions were present.", "small"), p("Eligible population, exceptions, and rate may be reported.", "small")],
        [p("Not Evaluable", "small"), p("A required analytical condition was absent.", "small"), p("Reason is reported and the exception rate remains blank.", "small")],
    ]
    story.append(styled_table(status_rows, [1.15 * inch, 2.85 * inch, 3.0 * inch], header=True, font_size=7.0, row_backgrounds=True))
    story.append(p(
        "A Not Evaluable test cannot appear as a clean zero-exception result. For every completed test, the framework reports the population actually eligible for that procedure so the result retains its denominator and scope.",
    ))

    story.extend([Spacer(1, 7), p("Configuration and reproducibility", "h2")])
    story.append(p(
        "Operational assumptions are stored outside the code in <font name='Courier'>config/defaults.json</font> and written to the run's calibration record. They include dates, activity windows, thresholds, minimum comparison populations, aging rules, tolerances, and review-priority weights. An institution must approve and test its own settings; bundled values are demonstration defaults.",
    ))

    # Page 3: control coverage and decision logic
    story.extend(section_page("2. What the Framework Tests"))
    story.append(p(
        "The 20 tests form a bounded reference set across three modules. They were selected to demonstrate how access, technology-operations, and payment-control objectives can be translated into transparent, repeatable procedures. The set is not a complete control catalog.",
    ))
    coverage = [
        ["Module", "Tests", "Records examined", "Examples of conditions identified"],
        [p("Privileged Access", "small"), p("PA-01 to PA-07<br/>(7 tests)", "small"),
         p("User status, access grants, and authentication activity", "small"),
         p("Access after termination or expiry, missing or self-approval, dormant access, entitlement conflicts, and unusual after-hours activity", "small")],
        [p("Change and Logging", "small"), p("CM-01 to CM-07<br/>(7 tests)", "small"),
         p("Change records, deployment events, and log-source heartbeats", "small"),
         p("Missing approval or test evidence, incompatible duties, unlinked deployments, unreviewed emergency changes, rate shifts, and logging gaps", "small")],
        [p("Reconciliation and Payments", "small"), p("TR-01 to TR-06<br/>(6 tests)", "small"),
         p("Ledger and processor-settlement records", "small"),
         p("Unmatched or aged items, amount differences, duplicate identifiers, unusual velocity, and activity below an approval limit", "small")],
    ]
    story.append(styled_table(
        coverage, [1.35 * inch, 0.9 * inch, 2.0 * inch, 2.75 * inch],
        header=True, font_size=6.9, row_backgrounds=True,
    ))

    story.extend([Spacer(1, 9), p("How the procedures decide", "h2")])
    story.append(p(
        "Most tests inspect each eligible record against a documented rule. For example, PA-07 reperforms the expiry check across active temporary privileged grants to determine whether any grant remained active after its approved expiry. Three procedures instead compare behavior across a supplied population:",
    ))
    comparisons = [
        ["Test", "Comparison", "Minimum analytical condition"],
        [p("PA-06", "small"), p("After-hours authentication counts across active privileged users", "small"), p("At least 30 active privileged users and usable variation", "small")],
        [p("CM-06", "small"), p("Recent emergency-change rate against an earlier baseline", "small"), p("10 recent changes, 30 baseline changes, and a nonzero baseline emergency count", "small")],
        [p("TR-05", "small"), p("Recent transaction counts across active accounts", "small"), p("At least 30 active accounts and usable variation", "small")],
    ]
    story.append(styled_table(comparisons, [0.7 * inch, 3.25 * inch, 3.05 * inch], header=True, font_size=6.9, row_backgrounds=True))
    story.append(p(
        "PA-06 and TR-05 use the median and median absolute deviation so a few extreme observations do not distort the comparison baseline. Every reported exception is a lead for investigation, not a confirmed control deviation, deficiency, intent, or culpability.",
    ))
    story.extend([Spacer(1, 7), p("Where the detailed work program lives", "h2")])
    story.append(p(
        "The complete practitioner procedure for each test - including its risk statement, intended control condition, eligible population, evidence examined, follow-up steps, tailoring points, and limitation - is documented in <font name='Courier'>docs/control-test-catalog.md</font>.",
    ))

    # Page 4: demonstration results and interpretation
    story.extend(section_page("3. What the Demonstration Showed"))
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
    story.extend([Spacer(1, 7), p("How to read counts and rates", "h2")])
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
    story.extend([Spacer(1, 8), p("What the output looks like", "h2")])
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

    # Page 5: interpretation, adoption, and governance
    story.extend(section_page("4. Moving from Exception to Institutional Use"))
    story.append(p(
        "A reported exception is the beginning of professional judgment, not the end of it. CCAF identifies the coded condition and preserves the evidence needed for follow-up; authorized personnel make the later determinations.",
    ))
    conclusion_steps = [
        ["Stage", "Meaning"],
        [p("1. Automated exception", "small"), p("The coded condition was met in the supplied eligible records.", "small")],
        [p("2. Investigated condition", "small"), p("A reviewer examined supporting records and relevant context.", "small")],
        [p("3. Confirmed deviation", "small"), p("The applicable control requirement was not performed as designed.", "small")],
        [p("4. Deficiency or finding", "small"), p("Authorized personnel evaluated the deviation under the institution's methodology.", "small")],
    ]
    story.append(styled_table(conclusion_steps, [1.85 * inch, 5.15 * inch], header=True, font_size=7.0, row_backgrounds=True))

    story.extend([Spacer(1, 7), p("Where CCAF fits", "h2")])
    lifecycle = [
        ["Assurance stage", "Responsibility"],
        [p("Before execution", "small"), p("Define the risk and control objective, confirm implementation, authorize access, establish source reliability, and approve configuration.", "small")],
        [p("CCAF execution", "small"), p("Apply the procedure, report status and eligible population, identify exceptions, and preserve run evidence.", "small")],
        [p("After execution", "small"), p("Investigate and disposition exceptions, determine remediation or escalation, and assess later changes for rollforward.", "small")],
    ]
    story.append(styled_table(lifecycle, [1.55 * inch, 5.45 * inch], header=True, font_size=7.0, row_backgrounds=True))
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

    # Page 6: boundaries, references, and release record
    story.extend(section_page("5. Boundaries, References, and Release Record"))
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
