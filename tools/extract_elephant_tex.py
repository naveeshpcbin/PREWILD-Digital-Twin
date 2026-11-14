import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"
bpy.ops.import_scene.gltf(filepath=p)

for img in bpy.data.images:
    print(f"Image name: {img.name}, size: {img.size}")
    out = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\extracted_elephant_tex.png"
    img.save_render(out)
    print("Saved extracted texture to", out)

