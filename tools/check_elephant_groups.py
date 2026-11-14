import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"
bpy.ops.import_scene.gltf(filepath=p)

mesh_obj = [o for o in bpy.data.objects if o.type == 'MESH' and 'Elephant' in o.name][0]
print("Mesh object name:", mesh_obj.name)
print("Mesh vertex count:", len(mesh_obj.data.vertices))
print("Vertex groups:", [vg.name for vg in mesh_obj.vertex_groups])

# Find average position of vertices in each vertex group
for vg in mesh_obj.vertex_groups:
    verts = [v.co for v in mesh_obj.data.vertices for g in v.groups if g.group == vg.index and g.weight > 0.5]
    if verts:
        avg_x = sum(v.x for v in verts) / len(verts)
        avg_y = sum(v.y for v in verts) / len(verts)
        avg_z = sum(v.z for v in verts) / len(verts)
        print(f"  Group '{vg.name}' ({len(verts)} verts): center = ({avg_x:.2f}, {avg_y:.2f}, {avg_z:.2f})")

