import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"
bpy.ops.import_scene.gltf(filepath=p)

# setup camera and lighting
cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_data.energy = 3.0
light_obj = bpy.data.objects.new(name="Sun", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(30), math.radians(45))

bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600

# View from Side (+Y looking at -Y)
cam_obj.location = (0, 7, 2)
cam_obj.rotation_euler = (math.radians(80), 0, math.radians(180))
bpy.context.scene.render.filepath = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\elephant_blender_render_side.png"
bpy.ops.render.render(write_still=True)

# View from +X (looking towards -X)
cam_obj.location = (7, 0, 2)
cam_obj.rotation_euler = (math.radians(80), 0, math.radians(90))
bpy.context.scene.render.filepath = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\elephant_blender_render_front.png"
bpy.ops.render.render(write_still=True)

# View from -X (looking towards +X)
cam_obj.location = (-7, 0, 2)
cam_obj.rotation_euler = (math.radians(80), 0, math.radians(-90))
bpy.context.scene.render.filepath = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\elephant_blender_render_back.png"
bpy.ops.render.render(write_still=True)
print("Rendered 3 views of elephant!")

