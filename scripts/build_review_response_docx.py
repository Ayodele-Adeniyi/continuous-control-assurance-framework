"""Build the Word review-response form from REVIEW_RESPONSE_TEMPLATE.md."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "REVIEW_RESPONSE_TEMPLATE.md"
OUTPUT = ROOT / "docs" / "CCAF_Independent_Review_Response_Template.docx"

NAVY = "193A5A"
LIGHT = "EAF0F5"
MID = "8EA2B3"
TEXT = RGBColor(28, 39, 49)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top: int = 90, start: int = 100, bottom: int = 90, end: int = 100) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        element = tc_mar.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            tc_mar.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def set_table_borders(table, color: str = MID, size: str = "6") -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def add_text(paragraph, text: str, *, bold: bool = False, italic: bool = False, size: float = 9.5, color=TEXT):
    run = paragraph.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return run


def add_heading(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(5)
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.keep_with_next = True
    add_text(paragraph, text, bold=True, size=11.5, color=RGBColor(25, 58, 90))


def parse_source() -> tuple[dict[str, str], list[tuple[str, str]], str, str]:
    text = SOURCE.read_text(encoding="utf-8")
    facts: dict[str, str] = {}
    for label, value in re.findall(r"^- \*\*(.+?):\*\*\s*(.+)$", text, flags=re.MULTILINE):
        facts[label] = value

    prompts: list[tuple[str, str]] = []
    for label, question in re.findall(
        r"^\*\*(.+?):\*\*\s*(.+?)\n\n\[Reviewer response\]",
        text,
        flags=re.MULTILINE,
    ):
        prompts.append((label, question))
    if len(prompts) != 4:
        raise ValueError(f"Expected four reviewer prompts in {SOURCE}, found {len(prompts)}")

    disclosure_match = re.search(
        r"^(This response may be cited publicly.+)$", text, flags=re.MULTILINE
    )
    confirmation_match = re.search(
        r"^(This response reflects my independent professional judgment.+)$",
        text,
        flags=re.MULTILINE,
    )
    if disclosure_match is None or confirmation_match is None:
        raise ValueError("Could not locate disclosure and confirmation language")
    return facts, prompts, disclosure_match.group(1), confirmation_match.group(1)


def add_prompt(doc: Document, label: str, question: str, *, box_height: float) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.keep_with_next = True
    add_text(paragraph, f"{label}: ", bold=True, size=9.4)
    add_text(paragraph, question, bold=True, size=9.4)

    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.columns[0].width = Inches(7.15)
    set_table_borders(table, color=MID, size="6")
    row = table.rows[0]
    row.height = Inches(box_height)
    row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
    cell = row.cells[0]
    cell.width = Inches(7.15)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    set_cell_margins(cell, top=100, start=110, bottom=100, end=110)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    add_text(paragraph, "[Type response here]", italic=True, size=9.2, color=RGBColor(100, 100, 100))


def build() -> Path:
    facts, prompts, disclosure, confirmation = parse_source()
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = TEXT
    normal.paragraph_format.space_after = Pt(2)
    normal.paragraph_format.line_spacing = 1.0

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(1)
    add_text(title, "INDEPENDENT TECHNICAL REVIEW RESPONSE", bold=True, size=15.5, color=RGBColor(25, 58, 90))
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(6)
    add_text(subtitle, "Continuous Control Assurance Framework (CCAF), Version 1.3.1", italic=True, size=10)

    intro = doc.add_paragraph()
    intro.paragraph_format.space_after = Pt(4)
    add_text(
        intro,
        "The release facts below are pre-filled for confirmation. Professional opinions must be written by the reviewer. Brief responses are acceptable; address only prompts relevant to the review performed.",
        size=9.2,
    )

    add_heading(doc, "1. Reviewer and scope")
    scope = doc.add_table(rows=3, cols=2)
    scope.autofit = False
    scope.columns[0].width = Inches(3.6)
    scope.columns[1].width = Inches(3.55)
    set_table_borders(scope)
    scope_rows = [
        ("Reviewer name and role: __________________________", "Relevant experience: __________________________"),
        ("Review date: __________________________", "Prior relationship, conflict, or compensation, if any: __________________"),
        ("Review depth: [ ] Focused  [ ] Detailed  [ ] Other: __________", "Release/commit examined: v1.3.1 / __________"),
    ]
    for row, values in zip(scope.rows, scope_rows):
        for cell, value in zip(row.cells, values):
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            add_text(paragraph, value, bold=True, size=8.8)

    add_heading(doc, "2. Release facts and procedures")
    release = doc.add_table(rows=5, cols=2)
    release.autofit = False
    release.columns[0].width = Inches(2.05)
    release.columns[1].width = Inches(5.10)
    set_table_borders(release)
    rows = [
        ("Repository and license", "github.com/Ayodele-Adeniyi/continuous-control-assurance-framework | Apache-2.0"),
        ("Documented scope", facts.get("Documented scope", "20 control tests using synthetic demonstration data")),
        ("Documented release claim", facts.get("Documented release claim", "165 of 165 deliberately planted conditions detected")),
        ("Focused command", facts.get("Focused reproduction command", "`python run_all.py --regenerate --no-charts`").strip("`")),
        ("Automated test command", facts.get("Automated test command", "`python -m unittest discover -s tests -v`").strip("`")),
    ]
    for row, (label, value) in zip(release.rows, rows):
        set_cell_shading(row.cells[0], LIGHT)
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell, top=65, bottom=65)
        add_text(row.cells[0].paragraphs[0], label, bold=True, size=8.7)
        add_text(row.cells[1].paragraphs[0], value, size=8.7)

    procedures = doc.add_paragraph()
    procedures.paragraph_format.space_before = Pt(3)
    procedures.paragraph_format.space_after = Pt(1)
    add_text(
        procedures,
        "Procedures personally performed:  [ ] Reproduced demonstration  [ ] Reviewed methodology/limitations  [ ] Ran tests  [ ] Inspected selected logic/artifacts",
        size=8.8,
    )
    corrections = doc.add_paragraph()
    corrections.paragraph_format.space_after = Pt(1)
    add_text(corrections, "Corrections to pre-filled facts, if any: ________________________________________________", size=8.8)
    observed = doc.add_paragraph()
    observed.paragraph_format.space_after = Pt(3)
    add_text(observed, "Result observed by reviewer, if reproduced: _____________________________________________", size=8.8)

    add_heading(doc, "3. Reviewer-authored professional opinion")
    add_prompt(doc, *prompts[0], box_height=1.25)
    add_prompt(doc, *prompts[1], box_height=1.25)

    doc.add_page_break()
    continuation = doc.add_paragraph()
    continuation.alignment = WD_ALIGN_PARAGRAPH.CENTER
    continuation.paragraph_format.space_after = Pt(5)
    add_text(continuation, "INDEPENDENT TECHNICAL REVIEW RESPONSE (CONTINUED)", bold=True, size=12.5, color=RGBColor(25, 58, 90))

    add_prompt(doc, *prompts[2], box_height=2.05)
    add_prompt(doc, *prompts[3], box_height=2.05)

    disclosure_paragraph = doc.add_paragraph()
    disclosure_paragraph.paragraph_format.space_before = Pt(7)
    disclosure_paragraph.paragraph_format.space_after = Pt(2)
    add_text(disclosure_paragraph, "Use disclosure: ", bold=True, italic=True, size=8.8)
    add_text(disclosure_paragraph, disclosure, italic=True, size=8.8)

    confirmation_paragraph = doc.add_paragraph()
    confirmation_paragraph.paragraph_format.space_after = Pt(7)
    confirmation_paragraph.paragraph_format.keep_with_next = True
    add_text(confirmation_paragraph, "Confirmation: ", bold=True, italic=True, size=8.8)
    add_text(confirmation_paragraph, confirmation, italic=True, size=8.8)

    signature = doc.add_table(rows=1, cols=3)
    signature.autofit = False
    widths = (2.25, 3.05, 1.85)
    for column, width in zip(signature.columns, widths):
        column.width = Inches(width)
    for index, (cell, text) in enumerate(zip(
        signature.rows[0].cells,
        ("Name: ____________________", "Signature: __________________________", "Date: ______________"),
    )):
        cell.width = Inches(widths[index])
        set_cell_margins(cell, top=70, bottom=70)
        add_text(cell.paragraphs[0], text, size=9.0)
    set_table_borders(signature, color="FFFFFF", size="0")

    doc.core_properties.title = "CCAF Independent Technical Review Response"
    doc.core_properties.subject = "Reviewer response form generated from REVIEW_RESPONSE_TEMPLATE.md"
    doc.core_properties.author = "Ayodele Timothy Adeniyi"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
