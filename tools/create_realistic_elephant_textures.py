from PIL import Image, ImageEnhance
import numpy as np
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
SRC_TEX = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\extracted_elephant_tex.png"

ALBEDO_OUT = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "elephant_albedo_realistic.png")
NORMAL_OUT = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "elephant_normal_realistic.png")

# 1. Load original texture
img = Image.open(SRC_TEX).convert("RGB")
w, h = img.size
arr = np.array(img, dtype=np.float32)

# Identify regions
mask_tusk = (arr[:, :, 0] > 185) & (arr[:, :, 1] > 185) & (arr[:, :, 2] > 185)
y_coords, x_coords = np.ogrid[:h, :w]
mask_eyes = ((x_coords - 495)**2 + (y_coords - 330)**2 <= 14**2)
mask_body = (~mask_tusk) & (~mask_eyes)

albedo = np.zeros_like(arr)
body_lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11) / 255.0

# Base skin: authentic Asian elephant slate-umber tone
base_r = 75.0 + (body_lum - 0.25) * 45.0
base_g = 71.0 + (body_lum - 0.25) * 42.0
base_b = 67.0 + (body_lum - 0.25) * 38.0

# Asian elephant depigmentation mottling
np.random.seed(42)
noise = np.random.rand(h, w)
pink_mask = mask_body & (noise > 0.94) & ((y_coords > 650) | ((x_coords < 350) & (y_coords > 400)))

albedo[:, :, 0] = np.where(pink_mask, 165.0 + noise * 30.0, base_r)
albedo[:, :, 1] = np.where(pink_mask, 120.0 + noise * 25.0, base_g)
albedo[:, :, 2] = np.where(pink_mask, 115.0 + noise * 20.0, base_b)

# Tusks: Warm aged ivory
albedo[mask_tusk, 0] = 248.0
albedo[mask_tusk, 1] = 242.0
albedo[mask_tusk, 2] = 218.0

# Eyes: Dark gloss amber
albedo[mask_eyes, 0] = 35.0
albedo[mask_eyes, 1] = 22.0
albedo[mask_eyes, 2] = 12.0

albedo = np.clip(albedo, 0, 255).astype(np.uint8)
albedo_img = Image.fromarray(albedo, mode="RGB")
albedo_img = ImageEnhance.Sharpness(albedo_img).enhance(1.3)
albedo_img.save(ALBEDO_OUT)
print(f"Saved realistic albedo: {ALBEDO_OUT}")

# 2. Tangent-Space Normal Map Generation from Wrinkle Bump using pure numpy
gray = np.array(albedo_img.convert("L"), dtype=np.float32)

# Compute gradients along Y and X
gy, gx = np.gradient(gray)

# Normal vector calculation: [-gx * strength, -gy * strength, 1.0]
strength = 4.0
nx = -gx * strength
ny = -gy * strength
nz = np.full_like(nx, 40.0)

length = np.sqrt(nx**2 + ny**2 + nz**2)
nx_norm = (nx / length * 127.5 + 127.5)
ny_norm = (ny / length * 127.5 + 127.5)
nz_norm = (nz / length * 127.5 + 127.5)

normal_arr = np.stack([nx_norm, ny_norm, nz_norm], axis=-1)
normal_arr = np.clip(normal_arr, 0, 255).astype(np.uint8)
normal_img = Image.fromarray(normal_arr, mode="RGB")
normal_img.save(NORMAL_OUT)
print(f"Saved realistic normal map: {NORMAL_OUT}")
