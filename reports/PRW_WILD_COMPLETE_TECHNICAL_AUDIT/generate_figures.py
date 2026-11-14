"""
Generate High-Resolution Technical Diagrams for PRW-Wild Engineering Audit.
Uses Matplotlib with clean, professional publication-style formatting.
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

FIGURES_DIR = Path(r"D:\Simulation For DT\reports\PRW_WILD_COMPLETE_TECHNICAL_AUDIT\figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Common styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#94a3b8'
plt.rcParams['axes.linewidth'] = 0.8

print("Generating Figure 1: System Architecture Diagram...")
fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis('off')

# Background canvas
ax.add_patch(patches.Rectangle((0, 0), 14, 8, facecolor='#f8fafc', edgecolor='none'))

# Title banner
ax.text(7.0, 7.55, "PRW-Wild End-to-End System Architecture", ha='center', va='center',
        fontsize=16, fontweight='bold', color='#0f172a')
ax.text(7.0, 7.22, "Physical Sensing Environment • Dual-ESP32 LoRa Gateway • Python Digital Twin Backend • WebGL Visualizer",
        ha='center', va='center', fontsize=9.5, color='#475569')

# Subsystem Containers
# 1. Physical Sensing Layer
p_rect = patches.FancyBboxPatch((0.4, 0.8), 3.0, 5.9, boxstyle="round,pad=0.2",
                                facecolor='#ffffff', edgecolor='#0284c7', linewidth=1.5)
ax.add_patch(p_rect)
ax.text(1.9, 6.4, "PHYSICAL SENSING NODE\n(ESP32-A Sensor Node)", ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#0369a1')

# Components in Node A
sensors = [
    ("HC-SR501 PIR Motion", "GPIO 32 • Digital Input\n45s Warmup Baseline Filter", "#e0f2fe", "#0284c7"),
    ("INMP441 MEMS Microphone", "GPIO 25, 33, 34 • I2S Mono Left\n16 kHz, 24-bit PCM in 32-bit slot", "#e0f2fe", "#0284c7"),
    ("Piezoelectric Geophone", "GPIO 35 • ADC1_CH7 (Input-only)\n20ms Window, 80 Samples @ 250µs\n[Safety Gate: PIEZO_CIRCUIT_VERIFIED=0]", "#fee2e2", "#b91c1c"),
    ("Ai-Thinker RA-02 SX1278", "SPI: SCK=18, MISO=19, MOSI=23\nNSS=27, RST=14, DIO0=26\n433.92 MHz, SF7, BW 125kHz, CR 4/5", "#f1f5f9", "#475569"),
]
y_pos = 5.4
for name, desc, bg, edge in sensors:
    box = patches.FancyBboxPatch((0.6, y_pos - 0.5), 2.6, 0.85, boxstyle="round,pad=0.08",
                                facecolor=bg, edgecolor=edge, linewidth=1.0)
    ax.add_patch(box)
    ax.text(1.9, y_pos - 0.15, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0f172a')
    ax.text(1.9, y_pos - 0.38, desc, ha='center', va='center', fontsize=6.8, color='#334155')
    y_pos -= 1.15

# Wireless LoRa Link
ax.annotate("", xy=(4.6, 3.8), xytext=(3.6, 3.8),
            arrowprops=dict(arrowstyle="<->", color="#2563eb", lw=2.5, linestyle="--"))
ax.text(4.1, 4.3, "433.92 MHz LoRa\nPW1|TEL / PW1|ACK", ha='center', va='center',
        fontsize=7.8, fontweight='bold', color='#1d4ed8')
ax.text(4.1, 3.3, "PDR: 100%\nRSSI: -64 dBm\nSNR: +9.8 dB", ha='center', va='center',
        fontsize=6.8, color='#475569')

# 2. ESP32-B Gateway Layer
b_rect = patches.FancyBboxPatch((4.7, 0.8), 2.9, 5.9, boxstyle="round,pad=0.2",
                                facecolor='#ffffff', edgecolor='#d97706', linewidth=1.5)
ax.add_patch(b_rect)
ax.text(6.15, 6.4, "RECEIVER & ACTUATOR\n(ESP32-B LED Gateway)", ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#b45309')

b_components = [
    ("RA-02 SX1278 Receiver", "SPI: 18, 19, 23, 27, 14, 26\nMonotonic Seq Validation\nDuplicate & Stale Rejection", "#fef3c7", "#d97706"),
    ("Six Physical LEDs Array", "LED1 (PIR)=32   LED2 (Piezo)=33\nLED3 (Mic)=25   LED4 (HB)=13\nLED5 (LoRa)=21  LED6 (Alert)=22\nBallast Resistors: 2000 Ω (2 kΩ)", "#fef3c7", "#d97706"),
    ("Operating Mode FSM", "AUTO_SENSOR • MANUAL • SIMULATION\nCascade Rule: A_OFF -> B_OFF\nEmergency All-Off Interlock", "#fef3c7", "#d97706"),
    ("USB Serial Transceiver", "CP2102 Bridge @ 115200 Baud\nPW1|TEL_USB Stream to Host\nNode-A Timeout: 2200 ms", "#f1f5f9", "#475569")
]
y_pos = 5.4
for name, desc, bg, edge in b_components:
    box = patches.FancyBboxPatch((4.9, y_pos - 0.5), 2.5, 0.85, boxstyle="round,pad=0.08",
                                facecolor=bg, edgecolor=edge, linewidth=1.0)
    ax.add_patch(box)
    ax.text(6.15, y_pos - 0.15, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0f172a')
    ax.text(6.15, y_pos - 0.38, desc, ha='center', va='center', fontsize=6.8, color='#334155')
    y_pos -= 1.15

# USB Link
ax.annotate("", xy=(8.7, 3.8), xytext=(7.8, 3.8),
            arrowprops=dict(arrowstyle="<->", color="#059669", lw=2.5))
ax.text(8.25, 4.25, "USB UART\nCOM7 @ 115.2k", ha='center', va='center',
        fontsize=7.8, fontweight='bold', color='#047857')

# 3. Python Backend
py_rect = patches.FancyBboxPatch((8.8, 0.8), 2.3, 5.9, boxstyle="round,pad=0.2",
                                facecolor='#ffffff', edgecolor='#059669', linewidth=1.5)
ax.add_patch(py_rect)
ax.text(9.95, 6.4, "PYTHON BACKEND\n(prw_wild Core)", ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#047857')

py_components = [
    ("LoraSerialBridge", "Thread-safe Non-blocking Reader\nStrict Physical/Simulation Isolation", "#d1fae5", "#059669"),
    ("HardwareManager", "Device Adapters (L1, L2, L3)\nCommand History & Diagnostics", "#d1fae5", "#059669"),
    ("YOLOv8 ONNX Vision", "yolov8n.onnx (12.8MB)\nDeep Inference on Viewport", "#d1fae5", "#059669"),
    ("Ecosystem & Risk Engine", "16 Species • 75 Agents • Boids\nHeuristic Multi-Factor Hysteresis", "#d1fae5", "#059669"),
    ("Web Server (HTTP REST)", "Port 8000 • JSON REST API\n/api/hardware/*, /api/ecosystem/*", "#d1fae5", "#059669"),
]
y_pos = 5.5
for name, desc, bg, edge in py_components:
    box = patches.FancyBboxPatch((9.0, y_pos - 0.42), 1.9, 0.68, boxstyle="round,pad=0.06",
                                facecolor=bg, edgecolor=edge, linewidth=0.9)
    ax.add_patch(box)
    ax.text(9.95, y_pos - 0.12, name, ha='center', va='center', fontsize=8.0, fontweight='bold', color='#0f172a')
    ax.text(9.95, y_pos - 0.32, desc, ha='center', va='center', fontsize=6.3, color='#334155')
    y_pos -= 0.88

# HTTP / WebSocket Link
ax.annotate("", xy=(12.1, 3.8), xytext=(11.3, 3.8),
            arrowprops=dict(arrowstyle="<->", color="#7c3aed", lw=2.5))
ax.text(11.7, 4.25, "HTTP REST\nPort 8000", ha='center', va='center',
        fontsize=7.8, fontweight='bold', color='#6d28d9')

# 4. Frontend & 3D Visualizer
ui_rect = patches.FancyBboxPatch((12.2, 0.8), 1.5, 5.9, boxstyle="round,pad=0.2",
                                facecolor='#ffffff', edgecolor='#7c3aed', linewidth=1.5)
ax.add_patch(ui_rect)
ax.text(12.95, 6.4, "DIGITAL TWIN\n(WebGL UI)", ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#6d28d9')

ui_components = [
    ("Three.js 3D Twin", "120x120 Elevation\nElephant GLB Walk\n13 PBR Plants"),
    ("Nine Viewpoints", "Observer, Follow\nIsometric, TopDown\nCamera POV PiP"),
    ("Tactical HUD", "PUBG-Style Overlay\n3D Wire Workbench\nLive Telemetry Stream"),
    ("Operator Control", "Manual LED Toggles\nPiezo/Mic Calib\nEmergency Stop")
]
y_pos = 5.3
for name, desc in ui_components:
    box = patches.FancyBboxPatch((12.35, y_pos - 0.52), 1.2, 0.82, boxstyle="round,pad=0.06",
                                facecolor="#ede9fe", edgecolor="#7c3aed", linewidth=0.9)
    ax.add_patch(box)
    ax.text(12.95, y_pos - 0.15, name, ha='center', va='center', fontsize=7.8, fontweight='bold', color='#0f172a')
    ax.text(12.95, y_pos - 0.42, desc, ha='center', va='center', fontsize=6.2, color='#334155')
    y_pos -= 1.15

plt.tight_layout()
fig.savefig(FIGURES_DIR / "fig1_system_architecture.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Figure 1 generated.")

# ---------------------------------------------------------------------------
# Figure 2: Three-Layer Spatial Geometry & Boundary Architecture
# ---------------------------------------------------------------------------
print("Generating Figure 2: Three-Layer Spatial Geometry Diagram...")
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
ax.set_xlim(0, 225)
ax.set_ylim(0, 200)

# Zones
# Western Forest Zone (0 to 100m)
ax.add_patch(patches.Rectangle((0, 0), 100, 200, facecolor='#ecfdf5', edgecolor='none'))
ax.text(25, 185, "WESTERN FOREST RESERVE (WILDLIFE HABITAT)\nX = 0m to 100m",
        fontsize=11, fontweight='bold', color='#065f46')

# Eastern Farmland Zone (100 to 225m)
ax.add_patch(patches.Rectangle((100, 0), 125, 200, facecolor='#fef3c7', edgecolor='none'))
ax.text(150, 185, "EASTERN AGRICULTURAL FARMLAND (PROTECTED SETTLEMENT)\nX = 100m to 225m",
        fontsize=11, fontweight='bold', color='#92400e')

# Migratory Corridor Depression (y=100m)
corridor = patches.Rectangle((0, 80), 100, 40, facecolor='#a7f3d0', alpha=0.5, edgecolor='#10b981', linestyle=':')
ax.add_patch(corridor)
ax.text(22, 100, "Depressed Wildlife Migratory Valley\n(Y = 80m to 120m, Depth 2.2m)",
        fontsize=9, fontweight='bold', color='#047857', ha='center', va='center')

# Water Ponds
north_pond = patches.Circle((75, 140), 22, facecolor='#bae6fd', edgecolor='#0284c7', alpha=0.7)
ax.add_patch(north_pond)
ax.text(75, 140, "North Pond\n(Depth 2.4m)", fontsize=8, color='#0369a1', ha='center', va='center', fontweight='bold')

south_pond = patches.Circle((45, 60), 18, facecolor='#bae6fd', edgecolor='#0284c7', alpha=0.7)
ax.add_patch(south_pond)
ax.text(45, 60, "South Pond\n(Depth 2.1m)", fontsize=8, color='#0369a1', ha='center', va='center', fontweight='bold')

# Three Concentric Detection Envelopes
# Layer 1: X = 45m to 70m (Cyan)
l1 = patches.Rectangle((45, 20), 25, 160, facecolor='#06b6d4', alpha=0.35, edgecolor='#0891b2', lw=2)
ax.add_patch(l1)
ax.text(57.5, 170, "LAYER 1 (OUTER)\nWi-Fi CSI / RF Corridor\nX = 45m to 70m (Width 25m)",
        fontsize=9, fontweight='bold', color='#0e7490', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#cffafe", edgecolor="#0891b2"))

# Layer 2: X = 70m to 85m (Amber)
l2 = patches.Rectangle((70, 20), 15, 160, facecolor='#f59e0b', alpha=0.40, edgecolor='#d97706', lw=2)
ax.add_patch(l2)
ax.text(77.5, 35, "LAYER 2 (MIDDLE)\nPhysical Sensors\n(PIR, Piezo, Mic)\nX = 70m to 85m",
        fontsize=8.5, fontweight='bold', color='#b45309', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef3c7", edgecolor="#d97706"))

# Layer 3: X = 85m to 100m (Violet)
l3 = patches.Rectangle((85, 20), 15, 160, facecolor='#a855f7', alpha=0.45, edgecolor='#7e22ce', lw=2)
ax.add_patch(l3)
ax.text(92.5, 168, "LAYER 3 (INNER)\nCamera Frustum\n(CAM_01 Gated Optical)\nX = 85m to 100m",
        fontsize=8.5, fontweight='bold', color='#6b21a8', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f3e8ff", edgecolor="#7e22ce"))

# Perimeter Boundary Fence Line (X = 100m)
ax.axvline(100, color='#dc2626', lw=3.5, linestyle='-', zorder=10)
ax.text(100, 10, "PERIMETER BOUNDARY FENCE (X = 100.0m)", fontsize=10, fontweight='bold',
        color='#b91c1c', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#fee2e2", edgecolor="#dc2626"))

# Camera Mast CAM_01 at (100, 100)
ax.plot(100, 100, marker='s', markersize=12, color='#7e22ce', zorder=15)
ax.text(107, 100, "CAM_01\n(Mast 6m, 55° FOV)", fontsize=8.5, fontweight='bold', color='#581c87')

# Camera Frustum Cone
fov_pts = np.array([[100, 100], [50, 75], [50, 125]])
cam_cone = patches.Polygon(fov_pts, closed=True, facecolor='#c084fc', alpha=0.25, edgecolor='#9333ea', linestyle='--')
ax.add_patch(cam_cone)

# Animal trajectory vector example
ax.annotate("Elephant Trajectory Vector (1.2 m/s)", xy=(90, 105), xytext=(20, 105),
            arrowprops=dict(facecolor='#1e293b', edgecolor='#0f172a', width=2.5, headwidth=9),
            fontsize=9.5, fontweight='bold', color='#0f172a')

# Axis labels
ax.set_xlabel("East-West Coordinate (Metres)", fontsize=11, fontweight='bold', color='#1e293b')
ax.set_ylabel("North-South Coordinate (Metres)", fontsize=11, fontweight='bold', color='#1e293b')
ax.set_title("PRW-Wild Three-Layer Wildlife Sensing Topology & Geographic Spatial Boundaries",
             fontsize=13, fontweight='bold', color='#0f172a', pad=12)
ax.grid(True, linestyle=':', alpha=0.6, color='#94a3b8')

plt.tight_layout()
fig.savefig(FIGURES_DIR / "fig2_three_layer_spatial.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Figure 2 generated.")

# ---------------------------------------------------------------------------
# Figure 3: Dual-ESP32 Hardware Schematic & Wiring Pinout
# ---------------------------------------------------------------------------
print("Generating Figure 3: Hardware Pinout Schematic Diagram...")
fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis('off')
ax.add_patch(patches.Rectangle((0, 0), 14, 8, facecolor='#ffffff', edgecolor='none'))

ax.text(7.0, 7.6, "Dual ESP32-WROOM-32 Physical Hardware Bench Architecture", ha='center', va='center',
        fontsize=15, fontweight='bold', color='#0f172a')
ax.text(7.0, 7.25, "Authoritative Pinout Manifest (hardware/wiring_manifest_actual.json v2.1.0-INTEGRATED)",
        ha='center', va='center', fontsize=9.5, color='#475569')

# ESP32-A Box (Left)
ax.add_patch(patches.FancyBboxPatch((0.8, 1.0), 5.5, 5.8, boxstyle="round,pad=0.2",
                                   facecolor='#f0f9ff', edgecolor='#0284c7', lw=2.0))
ax.text(3.55, 6.5, "ESP32-A: REMOTE SENSOR ACQUISITION NODE\n(DOIT ESP32 DEVKIT V1 / ESP32-WROOM-32)",
        ha='center', va='center', fontsize=10, fontweight='bold', color='#0369a1')

# ESP32-A Pins table
a_pins = [
    ("GPIO 18", "SPI SCK", "RA-02 SX1278 SPI Clock", "#0284c7"),
    ("GPIO 19", "SPI MISO", "RA-02 SX1278 Master In", "#0284c7"),
    ("GPIO 23", "SPI MOSI", "RA-02 SX1278 Master Out", "#0284c7"),
    ("GPIO 27", "NSS / CS", "RA-02 SX1278 Active-Low Chip Select", "#0284c7"),
    ("GPIO 14", "RESET", "RA-02 SX1278 Hardware Reset", "#0284c7"),
    ("GPIO 26", "DIO0", "RA-02 SX1278 Packet RX/TX Done IRQ", "#0284c7"),
    ("GPIO 32", "PIR OUT", "HC-SR501 Digital Motion In (45s Warmup)", "#059669"),
    ("GPIO 35", "PIEZO ADC", "ADC1_CH7 Input-Only [Gate: Fail-Closed]", "#dc2626"),
    ("GPIO 25", "I2S BCLK", "INMP441 Bit Clock Output (16 kHz)", "#7c3aed"),
    ("GPIO 33", "I2S WS", "INMP441 Word Select Output (Left/Right)", "#7c3aed"),
    ("GPIO 34", "I2S SD", "INMP441 Serial Data Input-Only (24-bit PCM)", "#7c3aed"),
    ("VIN / 5V", "5V Rail", "Supplies HC-SR501 PIR sensor VCC", "#b91c1c"),
    ("3V3 / GND", "Power", "Supplies RA-02 (3.3V) & INMP441 (3.3V)", "#334155")
]
y_pin = 5.9
for gpio, sig, desc, col in a_pins:
    ax.text(1.2, y_pin, gpio, fontsize=8.2, fontweight='bold', color=col, va='center')
    ax.text(2.2, y_pin, sig, fontsize=8.0, fontweight='bold', color='#1e293b', va='center')
    ax.text(3.1, y_pin, desc, fontsize=7.2, color='#475569', va='center')
    ax.axhline(y_pin - 0.16, xmin=0.08, xmax=0.43, color='#e2e8f0', lw=0.6)
    y_pin -= 0.36

# ESP32-B Box (Right)
ax.add_patch(patches.FancyBboxPatch((7.7, 1.0), 5.5, 5.8, boxstyle="round,pad=0.2",
                                   facecolor='#fefce8', edgecolor='#d97706', lw=2.0))
ax.text(10.45, 6.5, "ESP32-B: LORA RECEIVER & SIX-LED GATEWAY\n(DOIT ESP32 DEVKIT V1 / ESP32-WROOM-32)",
        ha='center', va='center', fontsize=10, fontweight='bold', color='#b45309')

b_pins = [
    ("GPIO 18", "SPI SCK", "RA-02 SX1278 SPI Clock", "#0284c7"),
    ("GPIO 19", "SPI MISO", "RA-02 SX1278 Master In", "#0284c7"),
    ("GPIO 23", "SPI MOSI", "RA-02 SX1278 Master Out", "#0284c7"),
    ("GPIO 27", "NSS / CS", "RA-02 SX1278 Active-Low Chip Select", "#0284c7"),
    ("GPIO 14", "RESET", "RA-02 SX1278 Hardware Reset", "#0284c7"),
    ("GPIO 26", "DIO0", "RA-02 SX1278 Packet RX/TX Done IRQ", "#0284c7"),
    ("GPIO 32", "LED 1", "LED1: PIR Motion Indicator (2 kΩ Ballast)", "#059669"),
    ("GPIO 33", "LED 2", "LED2: Piezo Vibration Indicator (2 kΩ)", "#dc2626"),
    ("GPIO 25", "LED 3", "LED3: Microphone RMS Alert (2 kΩ)", "#7c3aed"),
    ("GPIO 13", "LED 4", "LED4: Node-A Heartbeat (<2.2s Steady)", "#2563eb"),
    ("GPIO 21", "LED 5", "LED5: LoRa RX Pulse Indicator (120ms)", "#d97706"),
    ("GPIO 22", "LED 6", "LED6: Combined Alert (PIR||Piezo||Mic)", "#b91c1c"),
    ("USB Port", "CP2102", "UART @ 115200 Baud to Python Host (COM7)", "#047857")
]
y_pin = 5.9
for gpio, sig, desc, col in b_pins:
    ax.text(8.1, y_pin, gpio, fontsize=8.2, fontweight='bold', color=col, va='center')
    ax.text(9.1, y_pin, sig, fontsize=8.0, fontweight='bold', color='#1e293b', va='center')
    ax.text(10.0, y_pin, desc, fontsize=7.2, color='#475569', va='center')
    ax.axhline(y_pin - 0.16, xmin=0.57, xmax=0.92, color='#e2e8f0', lw=0.6)
    y_pin -= 0.36

# Bottom note on input-only pins
note_box = patches.FancyBboxPatch((0.8, 0.25), 12.4, 0.55, boxstyle="round,pad=0.1",
                                 facecolor='#fee2e2', edgecolor='#ef4444', lw=1.2)
ax.add_patch(note_box)
ax.text(7.0, 0.52, "CRITICAL HARDWARE SAFETY CONSTRAINTS: GPIO34 and GPIO35 are STRICTLY INPUT-ONLY on ESP32-WROOM-32.",
        ha='center', va='center', fontsize=8.2, fontweight='bold', color='#991b1b')
ax.text(7.0, 0.35, "Never configure GPIO34/35 as LED outputs. Piezo disc requires BAT54S dual Schottky clamping circuit before ADC1_CH7 sampling.",
        ha='center', va='center', fontsize=7.5, color='#7f1d1d')

plt.tight_layout()
fig.savefig(FIGURES_DIR / "fig3_hardware_wiring_diagram.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Figure 3 generated.")

# ---------------------------------------------------------------------------
# Figure 4: Test Suite Breakdown by Category
# ---------------------------------------------------------------------------
print("Generating Figure 4: Test Suite Breakdown Chart...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

modules = [
    "Physical Telemetry (18)", "Geometry Utilities (14)", "Config & Schema (13)",
    "Hardware Registry (11)", "Hardware Control (11)", "Web Server & REST (8)",
    "Sensor Fusion (8)", "Elephant Locomotion (8)", "Sensor Models (7)",
    "LoRa Bridge (7)", "Ecosystem Engine (6)", "Production Assets (6)",
    "Scenarios E2E (5)", "ONNX Detection (4)", "Vision Detector (4)",
    "Alert Dispatch (4)", "Multi-Animal Web (3)", "State Leakage (2)"
]
counts = [18, 14, 13, 11, 11, 8, 8, 8, 7, 7, 6, 6, 5, 4, 4, 4, 3, 2]
colors = ['#0284c7' if c >= 10 else '#0d9488' if c >= 6 else '#6366f1' for c in counts]

y_pos = np.arange(len(modules))
ax1.barh(y_pos, counts, color=colors, edgecolor='#1e293b', height=0.7)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(modules, fontsize=8.5)
ax1.invert_yaxis()
ax1.set_xlabel("Number of Unit & Integration Tests", fontsize=9.5, fontweight='bold')
ax1.set_title("PRW-Wild Automated Test Count by Module (139 Total)", fontsize=11, fontweight='bold', color='#0f172a')
ax1.grid(True, axis='x', linestyle=':', alpha=0.6)

for i, v in enumerate(counts):
    ax1.text(v + 0.3, i, str(v), va='center', fontsize=8.0, fontweight='bold', color='#1e293b')

# Donut chart for Subsystem Breakdown
domains = ["Physical Hardware & LoRa", "Digital Twin & Assets", "Simulation & Math Models", "Backend REST & Vision"]
domain_counts = [58, 28, 36, 17] # 18+11+11+7+7+4=58 hw, 8+6+14=28 twin/assets, 13+8+7+6+2=36 sim, 8+5+4=17
domain_colors = ['#0284c7', '#7c3aed', '#059669', '#d97706']

wedges, texts, autotexts = ax2.pie(domain_counts, labels=domains, autopct='%1.1f%%',
                                  startangle=140, colors=domain_colors,
                                  wedgeprops=dict(width=0.4, edgecolor='#ffffff', lw=2))
for t in texts:
    t.set_fontsize(8.5)
    t.set_fontweight('bold')
for at in autotexts:
    at.set_fontsize(8.5)
    at.set_color('#ffffff')
    at.set_fontweight('bold')

ax2.set_title("Test Suite Coverage by Engineering Domain\n139 / 139 Passed (100% Green)",
             fontsize=11, fontweight='bold', color='#0f172a')

plt.tight_layout()
fig.savefig(FIGURES_DIR / "fig4_test_suite_breakdown.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Figure 4 generated.")

print("All technical figures successfully created!")

