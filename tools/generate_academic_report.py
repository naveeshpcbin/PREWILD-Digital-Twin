"""PRW-Wild Academic Report Generator for Design Thinking (22ES390).

Generates the complete Design Thinking Mini Project Report using the exact
faculty-supplied Word template from Thiagarajar College of Engineering.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

# Import Report Content Modules
from report_content import (
    ABSTRACT_TEXT,
    CH1_SECTIONS,
    CH2_SECTIONS,
    LIT_TABLE_HEADERS,
    LIT_TABLE_ROWS,
    CH3_SECTIONS,
    CH4_SECTIONS,
    REQ_FR_HEADERS,
    REQ_FR_ROWS,
    REQ_NFR_HEADERS,
    REQ_NFR_ROWS,
    REQ_TRACE_HEADERS,
    REQ_TRACE_ROWS,
)
from report_content_part2 import (
    CH5_SECTIONS,
    SENSOR_REG_HEADERS,
    SENSOR_REG_ROWS,
    PINOUT_TABLE_HEADERS,
    PINOUT_TABLE_ROWS,
    CH6_SECTIONS,
    CH7_SECTIONS,
    CH8_SECTIONS,
    ITER_TABLE_HEADERS,
    ITER_TABLE_ROWS,
)
from report_content_part3 import (
    CH9_SECTIONS,
    TEAM_TABLE_HEADERS,
    TEAM_TABLE_ROWS,
    CH10_SECTIONS,
    CH11_SECTIONS,
    IEEE_REFERENCES,
    CH13_TEXT,
)

# Authoritative Paths
PROJECT_ROOT = Path(r"D:\Simulation For DT")
REPO_ROOT = PROJECT_ROOT / "prw-wild-digital-twin"
TEMPLATE_PATH = REPO_ROOT / "report" / "Mini project report template (2).docx"
OUTPUT_DIR_REPO = REPO_ROOT / "report" / "PRW_WILD_MINI_PROJECT_FINAL"
OUTPUT_DIR_ROOT = PROJECT_ROOT / "report" / "PRW_WILD_MINI_PROJECT_FINAL"

DOCX_OUT_PATH = OUTPUT_DIR_REPO / "PRW_WILD_MINI_PROJECT_REPORT.docx"
PDF_OUT_PATH = OUTPUT_DIR_REPO / "PRW_WILD_MINI_PROJECT_REPORT.pdf"

# Asset Paths for Figures
FIGURES_DIR = PROJECT_ROOT / "reports" / "PRW_WILD_COMPLETE_TECHNICAL_AUDIT" / "figures"
FIG_SYS_ARCH = FIGURES_DIR / "fig1_system_architecture.png"
FIG_SPATIAL = FIGURES_DIR / "fig2_three_layer_spatial.png"
FIG_WIRING = FIGURES_DIR / "fig3_hardware_wiring_diagram.png"
FIG_TESTS = FIGURES_DIR / "fig4_test_suite_breakdown.png"

# UI / Bench Assets
ARTIFACT_DIR = Path(r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283")
FIG_TWIN_UI = ARTIFACT_DIR / "shortest_website_view.png"
FIG_BENCH_PHOTO = ARTIFACT_DIR / "live_physical_bench_upgrade.png"


def set_run_font(run, name="Times New Roman", size_pt=12, bold=False, italic=False, color_rgb=(0, 0, 0)):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)


def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, name="Times New Roman", size_pt=16, bold=True)
    return p


def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, name="Times New Roman", size_pt=14, bold=True)
    return p


def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, name="Times New Roman", size_pt=12, bold=True)
    return p


def add_body_p(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.35
    p.paragraph_format.space_after = Pt(space_after)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_run_font(r_pre, name="Times New Roman", size_pt=12, bold=True)
    r_body = p.add_run(text)
    set_run_font(r_body, name="Times New Roman", size_pt=12, bold=False)
    return p


def add_bullet_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(4)
    r_bullet = p.add_run("•  ")
    set_run_font(r_bullet, name="Times New Roman", size_pt=12, bold=True)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_run_font(r_pre, name="Times New Roman", size_pt=12, bold=True)
    r_body = p.add_run(text)
    set_run_font(r_body, name="Times New Roman", size_pt=12, bold=False)
    return p


def add_figure(doc, img_path, caption, width_inches=5.6):
    if img_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_path), width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(12)
        p_cap.paragraph_format.keep_with_next = False
        run_cap = p_cap.add_run(caption)
        set_run_font(run_cap, name="Times New Roman", size_pt=11, bold=True, italic=True)
    else:
        p_err = doc.add_paragraph()
        p_err.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_err.add_run(f"[FIGURE ASSET NOT FOUND: {img_path.name}] - {caption}")
        set_run_font(run, name="Times New Roman", size_pt=11, bold=True, color_rgb=(180, 0, 0))


def add_styled_table(doc, headers, rows_data, col_widths=None):
    table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        shading = parse_xml(r'<w:shd {} w:fill="E2E8F0"/>'.format(nsdecls('w')))
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            set_run_font(run, name="Times New Roman", size_pt=10, bold=True)

    # Data Rows
    for r_idx, r_data in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(r_data):
            row_cells[c_idx].text = str(val)
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            align = WD_ALIGN_PARAGRAPH.CENTER if (c_idx == 0 or len(str(val)) < 15) else WD_ALIGN_PARAGRAPH.LEFT
            p.alignment = align
            for run in p.runs:
                set_run_font(run, name="Times New Roman", size_pt=9.5, bold=False)

    # Column widths
    if col_widths and len(col_widths) == len(headers):
        for row in table.rows:
            for c_idx, w in enumerate(col_widths):
                row.cells[c_idx].width = Inches(w)

    p_post = doc.add_paragraph()
    p_post.paragraph_format.space_after = Pt(8)


def process_front_matter(doc):
    """Updates Cover Page, Bonafide Certificate, Abstract, and Contents table in place."""
    print("Updating front matter...")

    # 1. Cover Page Title (P00)
    p0 = doc.paragraphs[0]
    p0.text = "PRW-WILD: A MULTI-LAYER WILDLIFE MONITORING AND IMMERSIVE DIGITAL TWIN SYSTEM"
    for r in p0.runs:
        set_run_font(r, name="Times New Roman", size_pt=15, bold=True)
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 2. Cover Page Student info (P06)
    p6 = doc.paragraphs[6]
    p6.text = "<<<Student Name>>> (<<<Register No.>>>)"
    for r in p6.runs:
        set_run_font(r, name="Times New Roman", size_pt=15, bold=True)
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 3. Bonafide Certificate Text (P24)
    p24 = doc.paragraphs[24]
    p24.text = (
        'Certified that this mini project report "PRW-WILD: A MULTI-LAYER WILDLIFE MONITORING AND IMMERSIVE DIGITAL TWIN SYSTEM" '
        'is the bonafide work of "<<<Student Name>>> (<<<Register No.>>>)" who carried out the mini project work as part of '
        'DESIGN THINKING (22ES390) under my supervision during the Academic Year 2026- 2027.'
    )
    for r in p24.runs:
        set_run_font(r, name="Times New Roman", size_pt=14, bold=False)
    p24.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 4. Abstract Section (P30 to P46)
    # P30 is 'ABSTRACT'. Insert Abstract text into P31.
    p31 = doc.paragraphs[31]
    p31.text = ABSTRACT_TEXT
    for r in p31.runs:
        set_run_font(r, name="Times New Roman", size_pt=12, bold=False)
    p31.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p31.paragraph_format.line_spacing = 1.35
    p31.paragraph_format.space_before = Pt(12)
    p31.paragraph_format.space_after = Pt(12)

    # Remove redundant empty paragraphs between P32 and P46 to prevent blank pages
    to_remove = doc.paragraphs[32:47]
    for p in to_remove:
        p._element.getparent().remove(p._element)

    # After removal, find 'Content' paragraph and ensure it starts cleanly on the next page
    for p in doc.paragraphs:
        if p.text.strip() == "Content":
            p.paragraph_format.page_break_before = True
            break


def build_all_chapters(doc):
    """Appends all 13 comprehensive academic chapters to the document."""
    print("Building Chapter 1: Introduction...")
    # Note: Chapter 1 begins after the template's Table of Contents page break
    add_heading_1(doc, "CHAPTER 1 — INTRODUCTION")
    for sec in CH1_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)

    print("Building Chapter 2: Literature Survey...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 2 — LITERATURE SURVEY")
    for sec in CH2_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "subsections" in sec:
            for sub in sec["subsections"]:
                add_heading_3(doc, sub["title"])
                add_body_p(doc, sub["text"])
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)
        if sec["title"] == "2.4 Critical Comparison of Existing Approaches vs. PRW-Wild":
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cap.add_run("Table 2.1: Critical Comparison of Existing Wildlife Monitoring Methodologies vs. PRW-Wild")
            set_run_font(r_c, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, LIT_TABLE_HEADERS, LIT_TABLE_ROWS, [1.1, 1.1, 1.1, 1.1, 1.1, 1.1])

    print("Building Chapter 3: Problem Statement and Objectives...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 3 — PROBLEM STATEMENT AND OBJECTIVES")
    for sec in CH3_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)

    print("Building Chapter 4: Stakeholder Profiles and Requirements Analysis...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 4 — STAKEHOLDER PROFILES: PERSONA AND REQUIREMENTS")
    for sec in CH4_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "personas" in sec:
            for p_dict in sec["personas"]:
                add_heading_3(doc, p_dict["name"])
                add_body_p(doc, p_dict["role"], bold_prefix="Role & Demographic: ")
                add_body_p(doc, p_dict["responsibilities"], bold_prefix="Primary Responsibilities: ")
                add_body_p(doc, p_dict["pain_points"], bold_prefix="Pain Points & Frustrations: ")
                add_body_p(doc, p_dict["core_needs"], bold_prefix="Core Operational Needs: ")
                add_body_p(doc, p_dict["system_touchpoint"], bold_prefix="Interaction with PRW-Wild: ")
        if sec["title"] == "4.3 Requirements Engineering Matrix":
            # FR Table
            p_cap1 = doc.add_paragraph()
            p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r1 = p_cap1.add_run("Table 4.1: Functional Requirements Specification (FR-01 to FR-08)")
            set_run_font(r1, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, REQ_FR_HEADERS, REQ_FR_ROWS, [0.8, 3.2, 1.2, 1.4])

            # NFR Table
            p_cap2 = doc.add_paragraph()
            p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r2 = p_cap2.add_run("Table 4.2: Non-Functional Requirements Specification (NFR-01 to NFR-06)")
            set_run_font(r2, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, REQ_NFR_HEADERS, REQ_NFR_ROWS, [0.8, 2.8, 1.8, 1.2])

        if sec["title"] == "4.4 Traceability Matrix: Mapping Stakeholder Needs to Engineering Specifications":
            p_cap3 = doc.add_paragraph()
            p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r3 = p_cap3.add_run("Table 4.3: Engineering Traceability Matrix: Mapping Stakeholder Needs to Technical Specifications")
            set_run_font(r3, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, REQ_TRACE_HEADERS, REQ_TRACE_ROWS, [1.3, 1.8, 2.0, 1.5])

    print("Building Chapter 5: Methodologies to Solve the Problem — Analysis...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 5 — METHODOLOGIES TO SOLVE THE PROBLEM — ANALYSIS")
    for sec in CH5_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)
        if sec["title"] == "5.2 Overall System Architecture and Data Pipeline":
            add_figure(doc, FIG_SYS_ARCH, "Figure 5.1: Overall PRW-Wild System Architecture and Hierarchical Processing Pipeline", width_inches=5.8)
        if sec["title"] == "5.3 Detailed Three-Layer Sensing Architecture":
            add_figure(doc, FIG_SPATIAL, "Figure 5.2: Three-Layer Spatial Sensing Corridor and Predictive Defense Boundaries", width_inches=5.8)
        if sec["title"] == "5.4 Rigorous Sensor Specifications and Numerical Registers":
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cap.add_run("Table 5.1: Comprehensive Sensor Numerical Specification and Performance Register")
            set_run_font(r_c, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, SENSOR_REG_HEADERS, SENSOR_REG_ROWS, [1.1, 0.9, 0.8, 1.0, 1.0, 1.0, 0.8])
        if sec["title"] == "5.5 Dual-Node Embedded Hardware Architecture (ESP32-A and ESP32-B)":
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cap.add_run("Table 5.2: Authoritative GPIO Pinout and Interface Mapping for ESP32-A and ESP32-B")
            set_run_font(r_c, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, PINOUT_TABLE_HEADERS, PINOUT_TABLE_ROWS, [1.3, 1.6, 0.8, 1.0, 0.9, 1.0])
        if "equations" in sec:
            for eq in sec["equations"]:
                add_heading_3(doc, f"Equation {eq['num']}: {eq['name']}")
                p_eq = doc.add_paragraph()
                p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_eq.paragraph_format.space_before = Pt(4)
                p_eq.paragraph_format.space_after = Pt(4)
                r_eq = p_eq.add_run(f"    {eq['latex']}    ({eq['num']})")
                set_run_font(r_eq, name="Times New Roman", size_pt=11.5, bold=True, italic=True)
                add_body_p(doc, eq["desc"])

    print("Building Chapter 6: Application of Engineering Knowledge...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 6 — APPLICATION OF ENGINEERING KNOWLEDGE / APPLICATION AREAS OF YOUR PROPOSED IDEA")
    for sec in CH6_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)

    print("Building Chapter 7: Conceptual Design and Prototype...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 7 — CONCEPTUAL DESIGN AND PROTOTYPE")
    for sec in CH7_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)
        if sec["title"] == "7.2 Complete Hardware Schematics and Interconnections":
            add_figure(doc, FIG_WIRING, "Figure 7.1: Comprehensive Electrical Schematic and Interconnection Diagram for ESP32-A and ESP32-B", width_inches=5.8)
        if sec["title"] == "7.5 Immersive 3D Digital Twin Visualizer Prototype":
            add_figure(doc, FIG_TWIN_UI, "Figure 7.2: Immersive 3D Digital Twin Visualizer and Real-Time Physical Telemetry Interface", width_inches=5.8)
        if sec["title"] == "7.6 Physical Bench Assembly and Implementation Evidence":
            add_figure(doc, FIG_BENCH_PHOTO, "Figure 7.3: Physical Bench Prototype Setup with Dual ESP32 Nodes, LoRa Modules, and Multi-Sensor Interfaces", width_inches=5.8)

    print("Building Chapter 8: Outcome, Societal Relevance and Iterative Redesign...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 8 — OUTCOME, SOCIETAL RELEVANCE AND FEEDBACK FROM CUSTOMERS AND STAKEHOLDERS TO REDESIGN")
    for sec in CH8_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)
        if sec["title"] == "8.1 Key Engineering Outcomes Achieved":
            add_figure(doc, FIG_TESTS, "Figure 8.1: Test Suite Verification and Subsystem Pass Rate Breakdown (139/139 Passing)", width_inches=5.8)
        if sec["title"] == "8.3 Stakeholder Feedback and Iterative Design Enhancements":
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cap.add_run("Table 8.1: System Iteration History and Stakeholder-Driven Engineering Refinements")
            set_run_font(r_c, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, ITER_TABLE_HEADERS, ITER_TABLE_ROWS, [1.0, 1.4, 1.4, 1.5, 1.3])

    print("Building Chapter 9: Contribution of the Team Members...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 9 — CONTRIBUTION OF THE TEAM MEMBERS")
    for sec in CH9_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if sec["title"] == "9.2 Comprehensive Contribution Matrix":
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cap.add_run("Table 9.1: Comprehensive Team Member Contribution Matrix")
            set_run_font(r_c, name="Times New Roman", size_pt=10.5, bold=True, italic=True)
            add_styled_table(doc, TEAM_TABLE_HEADERS, TEAM_TABLE_ROWS, [1.0, 0.8, 1.2, 1.6, 1.0, 1.0])

    print("Building Chapter 10: Professional Ethics Followed...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 10 — PROFESSIONAL ETHICS FOLLOWED")
    for sec in CH10_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)

    print("Building Chapter 11: Conclusion and Future Work...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 11 — CONCLUSION AND FUTURE WORK")
    for sec in CH11_SECTIONS:
        add_heading_2(doc, sec["title"])
        for para in sec["paragraphs"]:
            add_body_p(doc, para)
        if "bullets" in sec:
            for b_pre, b_txt in sec["bullets"]:
                add_bullet_p(doc, b_txt, bold_prefix=b_pre)

    print("Building Chapter 12: References...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 12 — REFERENCES")
    for ref in IEEE_REFERENCES:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.15
        r_ref = p_ref.add_run(ref)
        set_run_font(r_ref, name="Times New Roman", size_pt=10.5, bold=False)

    print("Building Chapter 13: Plagiarism Report...")
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 13 — PLAGIARISM REPORT")
    for para in CH13_TEXT.split("\n\n"):
        if para.strip():
            if "---" in para or "INSTITUTIONAL" in para or "Course" in para or "Status" in para:
                p_box = doc.add_paragraph()
                p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_box.paragraph_format.space_after = Pt(4)
                r_b = p_box.add_run(para.strip())
                set_run_font(r_b, name="Times New Roman", size_pt=11, bold=True)
            else:
                add_body_p(doc, para.strip())


def main():
    print(f"Loading master faculty template from: {TEMPLATE_PATH}")
    doc = docx.Document(TEMPLATE_PATH)

    # Process Front Matter
    process_front_matter(doc)

    # Build Chapters
    build_all_chapters(doc)

    # Save to intermediate output
    OUTPUT_DIR_REPO.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_ROOT.mkdir(parents=True, exist_ok=True)

    print(f"Saving populated DOCX to: {DOCX_OUT_PATH}")
    doc.save(DOCX_OUT_PATH)
    print("DOCX successfully generated.")


if __name__ == "__main__":
    main()
