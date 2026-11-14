from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import os
import bpy

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
SRC_TEX = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\extracted_elephant_tex.png"
ENHANCED_TEX = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "elephant_albedo_enhanced.png")

# 1. Image Enhancement with PIL and NumPy
img = Image.open(SRC_TEX).convert("RGB")
arr = np.array(img, dtype=np.float32)

# Tusks are very bright (R > 200, G > 200, B > 200)
# Eyes are very dark (R < 30, G < 30, B < 30)
# Body is midtone charcoal (30 <= R <= 190)

mask_body = (arr[:, :, 0] >= 20) & (arr[:, :, 0] <= 190) & (arr[:, :, 1] >= 20) & (arr[:, :, 1] <= 190)
mask_tusk = (arr[:, :, 0] > 190) & (arr[:, :, 1] > 190) & (arr[:, :, 2] > 190)

# Brighten body from ~65 to ~125 with rich warm undertones (warm grey/slate with slight earthy brown)
enhanced = arr.copy()
# Red channel gets warm lift (1.8x)
enhanced[:, :, 0] = np.where(mask_body, np.clip(arr[:, :, 0] * 1.85, 0, 160), arr[:, :, 0])
# Green channel gets natural foliage reflection (1.75x)
enhanced[:, :, 1] = np.where(mask_body, np.clip(arr[:, :, 1] * 1.78, 0, 150), arr[:, :, 1])
# Blue channel (1.7x) creates authentic earthy slate elephant hide
enhanced[:, :, 2] = np.where(mask_body, np.clip(arr[:, :, 2] * 1.70, 0, 145), arr[:, :, 2])

# Tusks get rich ivory tone (warm light cream)
enhanced[:, :, 0] = np.where(mask_tusk, 252, enhanced[:, :, 0])
enhanced[:, :, 1] = np.where(mask_tusk, 246, enhanced[:, :, 1])
enhanced[:, :, 2] = np.where(mask_tusk, 225, enhanced[:, :, 2])

result_img = Image.fromarray(np.uint8(enhanced), mode="RGB")
# Slight sharpness boost for skin wrinkles
enhancer = ImageEnhance.Sharpness(result_img)
result_img = enhancer.enhance(1.4)
result_img.save(ENHANCED_TEX)
print(f"Saved enhanced elephant texture to {ENHANCED_TEX}")

# 2. Update Blender GLB files
ANIMALS_STATIC = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals")
ANIMALS_ASSETS = os.path.join(PROJECT_DIR, "assets", "animals")

target_glbs = ["asian_elephant_production.glb", "asian_elephant_bull.glb", "asian_elephant.glb"]

for g in target_glbs:
    static_p = os.path.join(ANIMALS_STATIC, g)
    if not os.path.exists(static_p):
        continue
    
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=static_p)
    
    # Remove any stray Icosphere or Cube
    for o in list(bpy.data.objects):
        if o.name in ['Icosphere', 'Cube', 'Sphere', 'Camera', 'Light'] and o.type == 'MESH':
            print(f"Removing stray object {o.name} from {g}")
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Assign enhanced texture to material
    for mat in bpy.data.materials:
        if 'Elephant' in mat.name or mat.name == 'Mesh_0':
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Roughness"].default_value = 0.65
                bsdf.inputs["Metallic"].default_value = 0.0
                # Find image texture node or create
                tex_node = None
                for n in nodes:
                    if n.type == 'TEX_IMAGE':
                        tex_node = n
                        break
                if not tex_node:
                    tex_node = nodes.new("ShaderNodeTexImage")
                    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
                
                new_img = bpy.data.images.load(ENHANCED_TEX)
                tex_node.image = new_img
                print(f"Assigned enhanced texture to {mat.name} in {g}")
                
    # Export updated GLB
    bpy.ops.export_scene.gltf(
        filepath=static_p,
        export_format='GLB',
        use_selection=False,
        export_apply=False, # keep armature modifier intact!
        export_materials='EXPORT',
        export_animations=True,
        export_yup=True
    )
    # Also save to assets dir
    asset_p = os.path.join(ANIMALS_ASSETS, g)
    if os.path.exists(os.path.dirname(asset_p)):
        bpy.ops.export_scene.gltf(
            filepath=asset_p,
            export_format='GLB',
            use_selection=False,
            export_apply=False,
            export_materials='EXPORT',
            export_animations=True,
            export_yup=True
        )
    print(f"Exported updated {g}!")

