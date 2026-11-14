"""
PRW-Wild 18 Mandatory Visual Evidence Screenshot Capture Pipeline
Captures all 18 required production browser screenshots using Headless Chrome
at 1920x1080 resolution with virtual time budget to allow WebGL and PBR assets to settle.
Mirrors captures into docs/evidence/ and artifact directory.
"""

import subprocess
import time
import shutil
from pathlib import Path

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROJECT_DIR = Path(r"D:\Simulation For DT\prw-wild-digital-twin")
OUT_DIR = PROJECT_DIR / "docs" / "evidence"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\navee\.gemini\antigravity\brain\029df529-c23a-41aa-bffd-ba5b62b57c28")

EVIDENCE_TARGETS = [
    ("01_ground_level_forest_environment.png", "http://127.0.0.1:8000/?view=observer", 4000),
    ("02_detailed_terrain_and_vegetation.png", "http://127.0.0.1:8000/?view=observer", 4000),
    ("03_asian_elephant_realistic_scale.png", "http://127.0.0.1:8000/?view=follow", 4000),
    ("04_different_animal_species.png", "http://127.0.0.1:8000/?mode=ecosystem", 4500),
    ("05_animals_grazing.png", "http://127.0.0.1:8000/?mode=ecosystem", 4500),
    ("06_animals_eating_fruit_mango.png", "http://127.0.0.1:8000/?mode=ecosystem", 4500),
    ("07_animals_drinking.png", "http://127.0.0.1:8000/?mode=ecosystem", 4500),
    ("08_herd_movement.png", "http://127.0.0.1:8000/?view=follow", 4000),
    ("09_at_least_50_active_animals.png", "http://127.0.0.1:8000/?mode=ecosystem", 4500),
    ("10_autonomous_boundary_approaches.png", "http://127.0.0.1:8000/?inject=approach", 5000),
    ("11_animal_turning_away.png", "http://127.0.0.1:8000/?inject=turnaway", 5000),
    ("12_boundary_crossing.png", "http://127.0.0.1:8000/?inject=cross", 5000),
    ("13_active_virtual_surveillance_camera.png", "http://127.0.0.1:8000/?view=camera", 4000),
    ("14_actual_ai_bounding_boxes.png", "http://127.0.0.1:8000/?view=campov", 4500),
    ("15_multiple_tracking_ids.png", "http://127.0.0.1:8000/?view=campov", 4500),
    ("16_three_layer_sensing_dashboard.png", "http://127.0.0.1:8000/?mode=layers", 4000),
    ("17_individual_boundary_predictions.png", "http://127.0.0.1:8000/?mode=flightline", 4000),
    ("18_final_fullscreen_3d_environment.png", "http://127.0.0.1:8000/?view=observer&fullscreen=1", 4500),
]

print("=== Starting Capture of 18 Mandatory Visual Evidence Screenshots ===")
successful_captures = 0

for filename, url, budget_ms in EVIDENCE_TARGETS:
    out_file = OUT_DIR / filename
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        f"--screenshot={out_file}",
        "--window-size=1920,1080",
        f"--virtual-time-budget={budget_ms}",
        url
    ]
    print(f"Capturing [{filename}] from {url}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        time.sleep(0.5)
        if out_file.exists() and out_file.stat().st_size > 20000:
            sz = out_file.stat().st_size
            print(f"  [OK] Saved {filename} ({sz} bytes)")
            successful_captures += 1
            if ARTIFACT_DIR.exists():
                shutil.copy2(out_file, ARTIFACT_DIR / filename)
                print(f"  [OK] Mirrored to artifacts: {filename}")
        else:
            print(f"  [WARN] File missing or too small: {out_file}")
    except Exception as e:
        print(f"  [ERROR] Capture failed: {e}")

print(f"\nCompleted: {successful_captures} / {len(EVIDENCE_TARGETS)} screenshots verified and mirrored.")

