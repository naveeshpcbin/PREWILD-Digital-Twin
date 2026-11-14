import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"
bpy.ops.import_scene.gltf(filepath=p)

# setup camera
cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Add three-point lighting
light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_data.energy = 4.0
light_obj = bpy.data.objects.new(name="Sun", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(30), math.radians(45))

light2_data = bpy.data.lights.new(name="Fill", type='SUN')
light2_data.energy = 2.0
light2_obj = bpy.data.objects.new(name="Fill", object_data=light2_data)
bpy.context.collection.objects.link(light2_obj)
light2_obj.rotation_euler = (math.radians(-30), math.radians(-45), math.radians(120))

bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 768

# Camera at -6 in X (looking directly at -X face), Y=2, Z=2
cam_obj.location = (-6.5, 2.5, 2.2)
cam_obj.rotation_euler = (math.radians(72), math.radians(0), math.radians(-70))

bpy.context.scene.render.filepath = r"C:\Users\navee\.gemini\antigravity\brain\f5908e20-83e2-46bf-bfd2-bb4ae4f60283\elephant_head_direct_view.png"
bpy.ops.render.render(write_still=True)
print("Rendered head view!")

