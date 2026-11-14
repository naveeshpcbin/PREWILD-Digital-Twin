"""
Build and Render PRW-Wild Engineering Audit PDF.
Reads HTML template or constructs it cleanly, inserts base64 images, and compiles via Chrome/Edge.
"""

import base64
import os
import subprocess
from pathlib import Path

REPORTS_DIR = Path(r"D:\Simulation For DT\reports\PRW_WILD_COMPLETE_TECHNICAL_AUDIT")
FIGURES_DIR = REPORTS_DIR / "figures"
HTML_PATH = REPORTS_DIR / "audit_report.html"
PDF_PATH = REPORTS_DIR / "PRW_WILD_COMPLETE_SYSTEM_ARCHITECTURE_AND_IMPLEMENTATION_AUDIT.pdf"

def get_base64(p: Path) -> str:
    with open(p, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

fig1 = get_base64(FIGURES_DIR / "fig1_system_architecture.png")
fig2 = get_base64(FIGURES_DIR / "fig2_three_layer_spatial.png")
fig3 = get_base64(FIGURES_DIR / "fig3_hardware_wiring_diagram.png")
fig4 = get_base64(FIGURES_DIR / "fig4_test_suite_breakdown.png")

# Read existing build_pdf_report.py to extract HTML text or rewrite cleanly
# Let's write the complete HTML content directly into audit_report.html without f-string issues.

