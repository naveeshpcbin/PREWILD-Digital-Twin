import bpy
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\grass\tall_grass_clump.glb"
bpy.ops.import_scene.gltf(filepath=p)
for m in bpy.data.materials:
    print('Material:', m.name)
    if m.use_nodes:
        for n in m.node_tree.nodes:
            print('  Node:', n.name, n.type)
            if n.type == 'TEX_IMAGE':
                print('    Image:', n.image.name if n.image else 'NO IMAGE', n.image.filepath if n.image else '', n.image.size if n.image else '')

