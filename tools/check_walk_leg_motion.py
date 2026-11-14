import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
p = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals\asian_elephant_production.glb"
bpy.ops.import_scene.gltf(filepath=p)

# Check all animations
for anim in bpy.data.actions:
    print("Animation:", anim.name)
    # Check if there are fcurves or curves
    if hasattr(anim, 'fcurves'):
        for fc in anim.fcurves:
            print(f"  fc: {fc.data_path}[{fc.array_index}]")
    elif hasattr(anim, 'curves'):
        for c in anim.curves:
            print(f"  curve: {c.data_path}")

# Let's inspect the armature bones at frame 0, 10, 20, 30, 40
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
scene = bpy.context.scene
for f in [0, 10, 20, 30, 40]:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    fl_bone = arm.pose.bones.get('Leg_FL')
    bl_bone = arm.pose.bones.get('Leg_BL')
    if fl_bone and bl_bone:
        fl_loc = arm.matrix_world @ fl_bone.matrix @ fl_bone.location
        bl_loc = arm.matrix_world @ bl_bone.matrix @ bl_bone.location
        print(f"Frame {f}: Leg_FL loc={fl_bone.rotation_quaternion or fl_bone.rotation_euler}, Leg_BL={bl_bone.rotation_quaternion or bl_bone.rotation_euler}")

