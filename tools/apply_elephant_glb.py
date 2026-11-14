import bpy
import os

PROJECT_DIR = r"D:\Simulation For DT\prw-wild-digital-twin"
ENHANCED_TEX = os.path.join(PROJECT_DIR, "src", "prw_wild", "web", "static", "assets", "animals", "elephant_albedo_enhanced.png")
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
        export_apply=False,
        export_materials='EXPORT',
        export_animations=True,
        export_yup=True
    )
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

