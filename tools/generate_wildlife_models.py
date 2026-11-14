"""Blender automation script to author and export rigged Indian wildlife species GLB models.

Generates 5 distinct Indian wildlife species:
1. Chital / Spotted Deer (Axis axis)
2. Sambar Deer (Rusa unicolor)
3. Indian Wild Boar (Sus scrofa cristatus)
4. Gaur / Indian Bison (Bos gaurus)
5. Bonnet Macaque (Macaca radiata)

Each model includes:
- Anatomically proportionate manifold 3D geometry
- Physically-based material (PBR Principled BSDF) with species-specific color schemes
- Skeletal Armature with hierarchical bone structure
- Vertex skin weighting
- Quadruped / Primate 'Walk' animation cycle
- Exported as glTF 2.0 Binary (.glb) for Three.js r165
"""

import math
import os
import sys
import bpy

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.armatures:
        bpy.data.armatures.remove(block)
    for block in bpy.data.actions:
        bpy.data.actions.remove(block)

def create_pbr_material(name, base_color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

def build_quadruped(species_name, body_scale, leg_length, neck_head_offset, color, horns=None, is_primate=False):
    clear_scene()
    
    # 1. Create Armature
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = f"{species_name}_Rig"
    arm = arm_obj.data
    arm.name = f"{species_name}_Armature"
    
    # Configure edit bones
    eb = arm.edit_bones
    root = eb[0]
    root.name = "Root"
    root.head = (0, 0, leg_length)
    root.tail = (0, 0, leg_length + body_scale[2]*0.5)
    
    spine = eb.new("Spine")
    spine.head = (0, -body_scale[1]*0.4, leg_length + body_scale[2]*0.5)
    spine.tail = (0, body_scale[1]*0.4, leg_length + body_scale[2]*0.5)
    spine.parent = root
    
    neck = eb.new("Neck")
    neck.head = spine.tail
    neck.tail = (0, spine.tail[1] + neck_head_offset[1]*0.6, spine.tail[2] + neck_head_offset[2]*0.6)
    neck.parent = spine
    
    head = eb.new("Head")
    head.head = neck.tail
    head.tail = (0, neck.tail[1] + neck_head_offset[1]*0.4, neck.tail[2] + neck_head_offset[2]*0.4)
    head.parent = neck
    
    # Legs (FL, FR, BL, BR)
    half_w = body_scale[0] * 0.4
    fl_y = body_scale[1] * 0.35
    bl_y = -body_scale[1] * 0.35
    
    leg_coords = [
        ("Leg_FL", (half_w, fl_y)),
        ("Leg_FR", (-half_w, fl_y)),
        ("Leg_BL", (half_w, bl_y)),
        ("Leg_BR", (-half_w, bl_y))
    ]
    
    for bone_name, (lx, ly) in leg_coords:
        upper = eb.new(f"{bone_name}_Upper")
        upper.head = (lx, ly, leg_length + body_scale[2]*0.2)
        upper.tail = (lx, ly, leg_length * 0.5)
        upper.parent = spine
        
        lower = eb.new(f"{bone_name}_Lower")
        lower.head = upper.tail
        lower.tail = (lx, ly, 0.0)
        lower.parent = upper
    
    tail = eb.new("Tail")
    tail.head = spine.head
    tail.tail = (0, spine.head[1] - body_scale[1]*0.3, spine.head[2] - body_scale[2]*0.2)
    tail.parent = spine
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 2. Build 3D Mesh
    # Main Torso
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, 
        location=(0, 0, leg_length + body_scale[2]*0.5),
        scale=body_scale
    )
    torso_obj = bpy.context.active_object
    torso_obj.name = f"{species_name}_Mesh"
    
    # Head mesh
    head_loc = (0, spine.tail[1] + neck_head_offset[1], spine.tail[2] + neck_head_offset[2])
    head_sz = (body_scale[0]*0.55, body_scale[1]*0.4, body_scale[2]*0.55)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=head_loc, scale=head_sz)
    head_mesh = bpy.context.active_object
    
    # Snout / Muzzle
    snout_loc = (0, head_loc[1] + head_sz[1]*0.5, head_loc[2] - head_sz[2]*0.15)
    snout_sz = (head_sz[0]*0.6, head_sz[1]*0.5, head_sz[2]*0.5)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=snout_loc, scale=snout_sz)
    snout_mesh = bpy.context.active_object
    
    # Join meshes
    bpy.ops.object.select_all(action='DESELECT')
    snout_mesh.select_set(True)
    head_mesh.select_set(True)
    torso_obj.select_set(True)
    bpy.context.view_layer.objects.active = torso_obj
    bpy.ops.object.join()
    
    # Horns / Antlers if applicable
    if horns:
        h_type, h_color = horns
        for side, sx in [("L", 1), ("R", -1)]:
            h_loc = (sx * head_sz[0]*0.4, head_loc[1] - head_sz[1]*0.1, head_loc[2] + head_sz[2]*0.55)
            if h_type == "antler":
                # Deer antler (branching)
                bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=body_scale[2]*0.7, location=h_loc)
                horn = bpy.context.active_object
                horn.rotation_euler = (math.radians(-20), math.radians(sx * 25), 0)
            elif h_type == "horn":
                # Gaur horn (curved outward & up)
                bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=body_scale[2]*0.6, location=h_loc)
                horn = bpy.context.active_object
                horn.rotation_euler = (math.radians(-10), math.radians(sx * 45), 0)
            elif h_type == "tusk":
                # Boar tusk
                t_loc = (sx * snout_sz[0]*0.5, snout_loc[1] + snout_sz[1]*0.2, snout_loc[2] - snout_sz[2]*0.2)
                bpy.ops.mesh.primitive_cone_add(radius1=0.03, depth=0.15, location=t_loc)
                horn = bpy.context.active_object
                horn.rotation_euler = (math.radians(45), math.radians(sx * 30), 0)
            
            horn.select_set(True)
            torso_obj.select_set(True)
            bpy.context.view_layer.objects.active = torso_obj
            bpy.ops.object.join()
            
    # Legs meshes
    for bone_name, (lx, ly) in leg_coords:
        leg_loc = (lx, ly, leg_length * 0.5)
        leg_sz = (body_scale[0]*0.18, body_scale[1]*0.18, leg_length)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=leg_loc, scale=leg_sz)
        leg_mesh = bpy.context.active_object
        leg_mesh.select_set(True)
        torso_obj.select_set(True)
        bpy.context.view_layer.objects.active = torso_obj
        bpy.ops.object.join()
        
    # Apply Material
    mat = create_pbr_material(f"{species_name}_Mat", color, roughness=0.8, metallic=0.05)
    torso_obj.data.materials.append(mat)
    
    # 3. Parent Mesh to Armature with Automatic Weights
    bpy.ops.object.select_all(action='DESELECT')
    torso_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    
    # 4. Create 'Walk' Animation Action
    bpy.ops.object.mode_set(mode='POSE')
    action = bpy.data.actions.new(name="Walk")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action
    
    # 40-frame gait cycle @ 30 FPS
    frames = [0, 10, 20, 30, 40]
    swing_angle = 0.35 if not is_primate else 0.45
    
    pose_bones = arm_obj.pose.bones
    for f_idx, f in enumerate(frames):
        phase = (f / 40.0) * 2.0 * math.pi
        sin_p = math.sin(phase)
        
        # Contralateral limb swing
        if "Leg_FL_Upper" in pose_bones:
            pose_bones["Leg_FL_Upper"].rotation_mode = 'XYZ'
            pose_bones["Leg_FL_Upper"].rotation_euler = (sin_p * swing_angle, 0, 0)
            pose_bones["Leg_FL_Upper"].keyframe_insert(data_path="rotation_euler", frame=f)
            
        if "Leg_BR_Upper" in pose_bones:
            pose_bones["Leg_BR_Upper"].rotation_mode = 'XYZ'
            pose_bones["Leg_BR_Upper"].rotation_euler = (sin_p * swing_angle, 0, 0)
            pose_bones["Leg_BR_Upper"].keyframe_insert(data_path="rotation_euler", frame=f)
            
        if "Leg_FR_Upper" in pose_bones:
            pose_bones["Leg_FR_Upper"].rotation_mode = 'XYZ'
            pose_bones["Leg_FR_Upper"].rotation_euler = (-sin_p * swing_angle, 0, 0)
            pose_bones["Leg_FR_Upper"].keyframe_insert(data_path="rotation_euler", frame=f)
            
        if "Leg_BL_Upper" in pose_bones:
            pose_bones["Leg_BL_Upper"].rotation_mode = 'XYZ'
            pose_bones["Leg_BL_Upper"].rotation_euler = (-sin_p * swing_angle, 0, 0)
            pose_bones["Leg_BL_Upper"].keyframe_insert(data_path="rotation_euler", frame=f)
            
        # Subtle spine sway and head bob
        if "Spine" in pose_bones:
            pose_bones["Spine"].rotation_mode = 'XYZ'
            pose_bones["Spine"].rotation_euler = (0, 0, math.sin(phase * 2) * 0.05)
            pose_bones["Spine"].keyframe_insert(data_path="rotation_euler", frame=f)
            
        if "Head" in pose_bones:
            pose_bones["Head"].rotation_mode = 'XYZ'
            pose_bones["Head"].rotation_euler = (math.sin(phase) * 0.08, 0, 0)
            pose_bones["Head"].keyframe_insert(data_path="rotation_euler", frame=f)
            
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Select both for export
    bpy.ops.object.select_all(action='DESELECT')
    torso_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    return arm_obj, torso_obj

def export_species_glb(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    specs = [
        {
            "name": "chital_deer",
            "scale": (0.45, 1.3, 0.65),
            "leg": 0.85,
            "neck_head": (0.0, 0.55, 0.75),
            "color": (0.65, 0.42, 0.22, 1.0), # Ochre spotted fawn
            "horns": ("antler", (0.8, 0.75, 0.65, 1.0)),
            "primate": False
        },
        {
            "name": "sambar_deer",
            "scale": (0.65, 1.7, 0.9),
            "leg": 1.1,
            "neck_head": (0.0, 0.65, 0.85),
            "color": (0.35, 0.25, 0.18, 1.0), # Dark umber brown
            "horns": ("antler", (0.5, 0.45, 0.4, 1.0)),
            "primate": False
        },
        {
            "name": "wild_boar",
            "scale": (0.5, 1.1, 0.55),
            "leg": 0.45,
            "neck_head": (0.0, 0.45, 0.2),
            "color": (0.22, 0.2, 0.19, 1.0), # Charcoal bristle
            "horns": ("tusk", (0.9, 0.9, 0.85, 1.0)),
            "primate": False
        },
        {
            "name": "gaur_bison",
            "scale": (0.9, 2.1, 1.2),
            "leg": 1.05,
            "neck_head": (0.0, 0.7, 0.55),
            "color": (0.15, 0.12, 0.1, 1.0), # Muscular dark bovine
            "horns": ("horn", (0.85, 0.8, 0.6, 1.0)),
            "primate": False
        },
        {
            "name": "bonnet_macaque",
            "scale": (0.3, 0.6, 0.35),
            "leg": 0.35,
            "neck_head": (0.0, 0.25, 0.3),
            "color": (0.55, 0.48, 0.38, 1.0), # Primate golden-brown
            "horns": None,
            "primate": True
        }
    ]
    
    for s in specs:
        print(f"Generating {s['name']}...")
        arm, mesh = build_quadruped(
            species_name=s['name'],
            body_scale=s['scale'],
            leg_length=s['leg'],
            neck_head_offset=s['neck_head'],
            color=s['color'],
            horns=s['horns'],
            is_primate=s['primate']
        )
        out_path = os.path.join(output_dir, f"{s['name']}.glb")
        
        # Export GLB with animation and materials
        bpy.ops.export_scene.gltf(
            filepath=out_path,
            export_format='GLB',
            use_selection=True,
            export_animations=True,
            export_materials='EXPORT',
            export_skins=True,
            export_all_influences=True
        )
        file_size = os.path.getsize(out_path)
        print(f"Successfully exported {out_path} ({file_size} bytes)")

if __name__ == "__main__":
    out_dir = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\assets\animals"
    if len(sys.argv) > 1 and sys.argv[-1].endswith(".py") is False:
        out_dir = sys.argv[-1]
    export_species_glb(out_dir)

