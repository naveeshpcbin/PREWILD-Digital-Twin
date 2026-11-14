import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"
bpy.ops.import_scene.gltf(filepath=p)

for act in bpy.data.actions:
    print(f"Action: {act.name}, length: {act.frame_range}")
    for fc in act.fcurves:
        # print bone and property
        prop = fc.data_path
        first_val = fc.keyframe_points[0].co[1] if fc.keyframe_points else None
        mid_val = fc.keyframe_points[len(fc.keyframe_points)//2].co[1] if fc.keyframe_points else None
        print(f"  Curve: {prop} [{fc.array_index}] keys={len(fc.keyframe_points)} f0={first_val:.3f} fmid={mid_val:.3f}")

