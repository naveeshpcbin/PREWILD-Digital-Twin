"""Captures production verification screenshots using headless Chrome."""
import subprocess
import time
import shutil
from pathlib import Path

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = Path(r"D:\Simulation For DT\prw-wild-digital-twin\docs\evidence")
out_dir.mkdir(parents=True, exist_ok=True)
artifact_dir = Path(r"C:\Users\navee\.gemini\antigravity\brain\029df529-c23a-41aa-bffd-ba5b62b57c28")

targets = [
    ("01_main_world_overview.png", "http://127.0.0.1:8000/"),
    ("02_mode_f_multi_animal_ecosystem.png", "http://127.0.0.1:8000/?mode=ecosystem"),
    ("03_camera_ai_vision_monitor.png", "http://127.0.0.1:8000/?view=campov"),
    ("04_boundary_approach_trajectory.png", "http://127.0.0.1:8000/?inject=approach"),
    ("05_mode_e_hardware_lab_verified.png", "http://127.0.0.1:8000/?mode=hardware"),
    ("06_2d_spatial_radar_multi_animal.png", "http://127.0.0.1:8000/?view=2d"),
    ("08_production_world_nature_overview.png", "http://127.0.0.1:8000/?mode=ecosystem"),
]

for filename, url in targets:
    out_file = out_dir / filename
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        f"--screenshot={out_file}",
        "--window-size=1920,1080",
        "--virtual-time-budget=5000",
        url
    ]
    print(f"Capturing {filename} from {url}...")
    subprocess.run(cmd, capture_output=True, text=True)
    time.sleep(1)
    if out_file.exists():
        print(f"  [OK] Saved {filename} ({out_file.stat().st_size} bytes)")
        if artifact_dir.exists():
            shutil.copy2(out_file, artifact_dir / filename)
            print(f"  [OK] Mirrored to artifact dir: {filename}")
    else:
        print(f"  [FAIL] Could not capture {filename}")

print("All captures completed and synchronized to artifacts directory.")
