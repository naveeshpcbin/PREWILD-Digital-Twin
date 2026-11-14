import bpy

bpy.ops.wm.open_mainfile(filepath=r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\vegetation\fern_02.blend")

for img in bpy.data.images:
    print(f"Image: {img.name}, packed: {img.packed_file is not None}, size={img.size}")

