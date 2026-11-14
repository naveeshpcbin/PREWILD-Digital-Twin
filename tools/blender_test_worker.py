
import bpy
import os

print("[BLENDER WORKER] Initializing Blender Python execution test...")

# Reset to clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a test benchmark mesh (Suzanne monkey head + test pedestal)
bpy.ops.mesh.primitive_monkey_add(size=2.0, location=(0, 0, 1.5))
monkey = bpy.context.active_object
monkey.name = "Benchmark_Monkey"

# Add PBR material
mat = bpy.data.materials.new(name="M_Test_PBR")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.7, 0.4, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
monkey.data.materials.append(mat)

# Export to GLB
glb_path = r"D:\\Simulation For DT\\prw-wild-digital-twin\\assets\\test_output.glb"
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=False,
    export_apply=True
)
print(f"[BLENDER WORKER] Exported test GLB to D:\\Simulation For DT\\prw-wild-digital-twin\\assets\\test_output.glb")

# Test re-importing GLB
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)
imported_count = len(bpy.data.objects)
print(f"[BLENDER WORKER] Re-imported GLB successfully. Scene objects count: {imported_count}")

# Save .blend project file
blend_path = r"D:\\Simulation For DT\\prw-wild-digital-twin\\assets\\test_project.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[BLENDER WORKER] Saved Blender project file to D:\\Simulation For DT\\prw-wild-digital-twin\\assets\\test_project.blend")
print("[BLENDER WORKER] ALL BLENDER WORKER TASKS COMPLETED!")
