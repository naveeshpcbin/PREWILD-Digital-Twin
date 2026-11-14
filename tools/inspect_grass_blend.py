import bpy

bpy.ops.wm.open_mainfile(filepath=r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\vegetation\grass_medium_01.blend")
print("Objects in grass_medium_01.blend:")
for o in bpy.data.objects:
    print(f"  {o.name} ({o.type})")

print("Images:")
for img in bpy.data.images:
    print(f"  {img.name}, size={img.size}, filepath={img.filepath}")

print("Materials:")
for mat in bpy.data.materials:
    print(f"  {mat.name}")

