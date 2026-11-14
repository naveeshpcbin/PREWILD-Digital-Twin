import bpy
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\vegetation\forest_ferns.glb"
bpy.ops.import_scene.gltf(filepath=p)

for i, img in enumerate(bpy.data.images):
    print(f"Fern image {i}: {img.name}, size={img.size}")
    out = rf"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\fern_tex_{i}.png"
    img.save_render(out)
    print("Saved to", out)

