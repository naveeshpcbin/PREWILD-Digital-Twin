import bpy

bpy.ops.wm.open_mainfile(filepath=r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\vegetation\grass_medium_01.blend")

for img in bpy.data.images:
    print(f"Image: {img.name}, packed: {img.packed_file is not None}, size={img.size}")
    if img.packed_file or (img.size[0] > 0 and img.size[1] > 0):
        out_p = rf"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\environment\vegetation\{img.name}"
        if not out_p.endswith('.png') and not out_p.endswith('.jpg'):
            out_p += '.png'
        try:
            img.save_render(out_p)
            print(f"  Extracted to {out_p}")
        except Exception as e:
            print(f"  Error extracting: {e}")

