import bpy
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"
bpy.ops.import_scene.gltf(filepath=p)

for obj in bpy.data.objects:
    print(f"Object: {obj.name}, type: {obj.type}")
    if obj.type == 'ARMATURE':
        for bone in obj.data.bones:
            print(f"  Bone: {bone.name}, head={bone.head}, tail={bone.tail}")
    elif obj.type == 'MESH':
        coords = [v.co for v in obj.data.vertices]
        min_x = min(c.x for c in coords)
        max_x = max(c.x for c in coords)
        min_y = min(c.y for c in coords)
        max_y = max(c.y for c in coords)
        min_z = min(c.z for c in coords)
        max_z = max(c.z for c in coords)
        print(f"  Mesh bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}], Z=[{min_z:.2f}, {max_z:.2f}]")

