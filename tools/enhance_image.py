from PIL import Image, ImageEnhance
import numpy as np
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
SRC_TEX = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\extracted_elephant_tex.png"
ENHANCED_TEX = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "elephant_albedo_enhanced.png")

# 1. Image Enhancement with PIL and NumPy
img = Image.open(SRC_TEX).convert("RGB")
arr = np.array(img, dtype=np.float32)

mask_body = (arr[:, :, 0] >= 15) & (arr[:, :, 0] <= 190) & (arr[:, :, 1] >= 15) & (arr[:, :, 1] <= 190)
mask_tusk = (arr[:, :, 0] > 190) & (arr[:, :, 1] > 190) & (arr[:, :, 2] > 190)

enhanced = arr.copy()
# Red channel gets warm lift (1.9x) - authentic warm Asian elephant skin tone
enhanced[:, :, 0] = np.where(mask_body, np.clip(arr[:, :, 0] * 1.95, 0, 165), arr[:, :, 0])
# Green channel (1.85x)
enhanced[:, :, 1] = np.where(mask_body, np.clip(arr[:, :, 1] * 1.88, 0, 155), arr[:, :, 1])
# Blue channel (1.75x) creates authentic earthy slate elephant hide
enhanced[:, :, 2] = np.where(mask_body, np.clip(arr[:, :, 2] * 1.78, 0, 148), arr[:, :, 2])

# Tusks get rich ivory tone (warm light cream)
enhanced[:, :, 0] = np.where(mask_tusk, 252, enhanced[:, :, 0])
enhanced[:, :, 1] = np.where(mask_tusk, 246, enhanced[:, :, 1])
enhanced[:, :, 2] = np.where(mask_tusk, 225, enhanced[:, :, 2])

result_img = Image.fromarray(np.uint8(enhanced), mode="RGB")
enhancer = ImageEnhance.Sharpness(result_img)
result_img = enhancer.enhance(1.4)
result_img.save(ENHANCED_TEX)
print(f"Saved enhanced elephant texture to {ENHANCED_TEX}")

