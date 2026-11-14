import bpy
import os

animals_dir = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals"
files = sorted([f for f in os.listdir(animals_dir) if f.endswith('.glb')])

for f in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    p = os.path.join(animals_dir, f)
    try:
        bpy.ops.import_scene.gltf(filepath=p)
        mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
        arm_objs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
        
        head_pos = None
        tail_pos = None
        if arm_objs:
            arm = arm_objs[0]
            for b in arm.data.bones:
                if 'head' in b.name.lower():
                    head_pos = [round(v, 2) for v in b.head]
                if 'tail' in b.name.lower():
                    tail_pos = [round(v, 2) for v in b.head]
        
        # Check mesh bounds
        if mesh_objs:
            m = mesh_objs[0]
            coords = [v.co for v in m.data.vertices]
            min_x, max_x = min(c.x for c in coords), max(c.x for c in coords)
            min_y, max_y = min(c.y for c in coords), max(c.y for c in coords)
            min_z, max_z = min(c.z for c in coords), max(c.z for c in coords)
            print(f"{f}: bounds X=[{min_x:.1f},{max_x:.1f}] Y=[{min_y:.1f},{max_y:.1f}] Z=[{min_z:.1f},{max_z:.1f}] | Head={head_pos} | Tail={tail_pos}")
    except Exception as e:
        print(f"{f}: ERROR {e}")

