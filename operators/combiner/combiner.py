import bpy
from bpy.props import *

from .combiner_ops import *
from .packer import BinPacker
from ... import globs


class Combiner(bpy.types.Operator):
    bl_idname = 'smc.combiner'
    bl_label = 'Create Atlas'
    bl_description = 'Combine materials'
    bl_options = {'UNDO', 'INTERNAL'}

    directory = StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob = StringProperty(default='', options={'HIDDEN'})
    cats = BoolProperty(default=False)
    data = None
    mats_uv = None
    structure = None

    def execute(self, context: bpy.types.Context) -> Set[str]:
        if not self.data:
            self.invoke(context, None)
        scn = context.scene
        scn.smc_save_path = self.directory
        self.structure = BinPacker(get_size(scn, self.structure)).fit()

        size = get_atlas_size(self.structure)
        atlas_size = calculate_adjusted_size(scn, size)

        if max(atlas_size, default=0) > 20000:
            self.report({'ERROR'}, 'The output image size of {0}x{1}px is too large'.format(*atlas_size))
            return {'FINISHED'}

        atlas = get_atlas(scn, self.structure, atlas_size)
        align_uvs(scn, self.structure, atlas.size, size)
        comb_mats = get_comb_mats(scn, atlas, self.mats_uv)
        assign_comb_mats(scn, self.data, comb_mats)
        clear_mats(scn, self.mats_uv)
        bpy.ops.smc.refresh_ob_data()
        self.report({'INFO'}, 'Materials were combined')
        return {'FINISHED'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> Set[str]:
        scn = context.scene
        bpy.ops.smc.refresh_ob_data()

        if self.cats:
            scn.smc_size = 'PO2'
            scn.smc_gaps = 0

        set_ob_mode(context.view_layer if globs.is_blender_2_80_or_newer else scn, scn.smc_ob_data)
        self.data = get_data(scn.smc_ob_data)
        self.mats_uv = get_mats_uv(scn, self.data)
        clear_empty_mats(scn, self.data, self.mats_uv)
        get_duplicates(self.mats_uv)
        self.structure = get_structure(scn, self.data, self.mats_uv)

        if globs.is_blender_2_79_or_older:
            context.space_data.viewport_shade = 'MATERIAL'

        if len(self.structure) == 1 and next(iter(self.structure.values()))['dup']:
            clear_duplicates(scn, self.structure)
            return self._return_with_message('INFO', 'Duplicates were combined')
        elif not self.structure or len(self.structure) == 1:
            return self._return_with_message('ERROR', 'No unique materials selected')
        if event is not None:
            context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def _return_with_message(self, message_type: str, message: str) -> Set[str]:
        bpy.ops.smc.refresh_ob_data()
        self.report({message_type}, message)
        return {'FINISHED'}

### Sable Tweaks
class Combiner_Sable(bpy.types.Operator):
    bl_idname = 'smc.combiner_sable'
    bl_label = 'Create Atlas - Sable'
    bl_description = 'Combine materials split by Sable\'s tweaks'
    bl_options = {'UNDO', 'INTERNAL'}

    directory = StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    #filter_glob = StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None

    errors = ""

    sableMaterialMap = {
        "Outfit" : ["HairClip", "FaceEyebrows"] # Forced Outfit Material names. Others types must not match against anything in this first before adding it to its type
        , "Body" : ["Body", "Mouth"]
        , "Transparents" : ["EyeReflections", "SunglassesLens", "FaceTransparents", "SwimmingGreenFrills"]        
        , "Blushables" : ["Face", "Ears", "SableFerretEar"]
        , "Emissives" : ["Eyes", "Cellphone", "Hair"]
        , "Emotes" : ["Emotes"]
    }

    def type_to_output_name_sable(self, scn: bpy.types.Context, type_name: str) -> str:
        if (type_name == "Body"):
            return str(scn.smc_sable_body_texture_name).strip()
    
        if (type_name == "Blushables"):
            return str(scn.smc_sable_blushables_texture_name).strip()
    
        if (type_name == "Transparents"):
            return str(scn.smc_sable_transparents_texture_name).strip()
    
        if (type_name == "Emissives"):
            return str(scn.smc_sable_emissive_texture_name).strip()
    
        if (type_name == "Emotes"):
            return str(scn.smc_sable_emotes_texture_name).strip()

        return str(scn.smc_sable_outfit_texture_name).strip()
    
    def type_to_create_atlas(self, scn: bpy.types.Context, type_name: str) -> str:
        if (type_name == "Body"):
            return scn.smc_sable_create_body_texture
    
        if (type_name == "Blushables"):
            return scn.smc_sable_create_blushables_texture
    
        if (type_name == "Transparents"):
            return scn.smc_sable_create_transparents_texture
    
        if (type_name == "Emissives"):
            return scn.smc_sable_create_emissive_texture
    
        if (type_name == "Emotes"):
            return scn.smc_sable_create_emotes_texture

        return scn.smc_sable_create_outfit_texture        

    def execute(self, context: bpy.types.Context) -> Set[str]:
        scn = context.scene
        scn.smc_save_path = self.directory

        errors = ""

        bpy.ops.smc.refresh_ob_data()

        #scn.smc_size = 'PO2'
        #scn.smc_gaps = 0

        set_ob_mode(context.view_layer if globs.is_blender_2_80_or_newer else scn, scn.smc_ob_data)

        # Merge by distance
        if scn.smc_sable_merge_by_distance_weight >= 0.0:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold = scn.smc_sable_merge_by_distance_weight)
            bpy.ops.mesh.select_all(action='DESELECT')

        set_ob_mode(context.view_layer if globs.is_blender_2_80_or_newer else scn, scn.smc_ob_data)

        # Handle shapkey cleanup
        for item in scn.smc_ob_data:
            if item.type == globs.CL_OBJECT:
                print("Object Found: " + item.ob.name)

                shapekeys = item.ob.data.shape_keys

                print("Shapkeys: " + str(shapekeys))
                keyblocks = shapekeys.key_blocks
                
                # Clear any and all keyblock values and vgroups
                index = 0
                while index < len(keyblocks):
                    keyblock = keyblocks[index]
                    keyblock.value = 0
                    keyblock.vertex_group = ""

                    index += 1

                index = 0
                while index < len(keyblocks):
                    keyblock = keyblocks[index]
                    keyblock_name = keyblock.name

                    print("Keyblock Name: " + keyblock_name)

                    if keyblock_name.endswith(" [X]"):
                        #item.ob.active_shape_key_index = index
                        item.ob.shape_key_remove(keyblock)
                        print("Removed Shapekey: " + keyblock_name)
                        
                        # Don't increase loop index cuz of removed shapkey
                        continue

                    if keyblock_name.endswith(" [M]"):
                        # Duplicate Shapekey, mirror the current shapekey, rename current to right variant, set duplicated shapekey's name to the original name

                        item.ob.active_shape_key_index = index

                        new_keyblock_name = keyblock_name[0:-4] # trim

                        keyblock.name = new_keyblock_name.replace("Left", "Right")

                        keyblock.value = 1

                        item.ob.shape_key_add(name=new_keyblock_name, from_mix=True)

                        keyblock.value = 0

                        bpy.ops.object.shape_key_mirror()
                        print("Mirrored Shapekey: " + new_keyblock_name + " into " + keyblock.name + " and " + new_keyblock_name)

                        # Move selected shapekey down to bottom of list
                        bpy.ops.object.shape_key_move(type='BOTTOM')                  

                        # Don't increase loop index cuz we moved the shapekey to the end of the array
                        continue

                    if keyblock_name.endswith(" [H]"):
                        new_keyblock_name = keyblock_name[0:-4] # trim

                        keyblock.value = 1
                        keyblock.vertex_group = "HeadLeftSide Smoothed [X]"
                        item.ob.shape_key_add(name=new_keyblock_name + "Left", from_mix=True)
                        keyblock.vertex_group = "HeadRightSide Smoothed [X]"                        
                        item.ob.shape_key_add(name=new_keyblock_name + "Right", from_mix=True)
                        keyblock.value = 0

                        item.ob.shape_key_remove(keyblock)

                        print("Split Shapekey: " + keyblock_name + " into " + new_keyblock_name + "Left" + new_keyblock_name + "Right. Removed split source: " + new_keyblock_name)
                        
                        # Don't increase loop index cuz of removed shapkey
                        continue

                    if keyblock_name.endswith(" [V]"):
                        new_keyblock_name = keyblock_name[0:-4] # trim

                        keyblock.value = 1
                        keyblock.vertex_group = "UpperMouthMask Smoothed [X]"
                        item.ob.shape_key_add(name=new_keyblock_name + "Upper", from_mix=True)
                        keyblock.vertex_group = "LowerMouthMask Smoothed [X]"                        
                        item.ob.shape_key_add(name=new_keyblock_name + "Lower", from_mix=True)
                        keyblock.value = 0

                        item.ob.shape_key_remove(keyblock)

                        print("Split Shapekey: " + keyblock_name + " into " + new_keyblock_name + "Upper" + new_keyblock_name + "Lower. Removed split source: " + new_keyblock_name)
                        
                        # Don't increase loop index cuz of removed shapkey
                        continue                    

                   
                    index += 1 
                    # TODO: Be on the lookout for shapekeys that have the same name. Need to merge them

        # Handle deleting [X] marked bones
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Need to switch into Edit mode with just the Armature's object selected
        armatureObject = None
        armature = None
        try:
            armatureObject = bpy.data.objects["Armature"]

            if armatureObject.type == 'ARMATURE':
                armature = armatureObject.data
        except KeyError:
            print("Armature of name 'Armature' was not found")

        if armature != None:
            armatureObject.select_set(True)
            bpy.context.view_layer.objects.active = armatureObject
            bpy.ops.object.mode_set(mode='EDIT')

            index = 0
            while index < len(armature.edit_bones):
                bone = armature.edit_bones[index]
                #print("Checking for Bone: " + bone.name)
                if bone.name.endswith(" [X]"):
                    boneName = bone.name
                    armature.edit_bones.remove(bone)
                    print("Removed Bone: " + boneName)
                    
                    # Don't increment loop index cuz of removed bone
                    continue
                index += 1

            armatureObject.update_from_editmode()
        set_ob_mode(context.view_layer if globs.is_blender_2_80_or_newer else scn, scn.smc_ob_data)

        #self.data = get_data_sable(scn.smc_ob_data)
        #self.mats_uv = get_mats_uv(scn, self.data)
        #clear_empty_mats(scn, self.data, self.mats_uv)
        
        
        # Ignore Duplicates
        #get_duplicates(self.mats_uv)
        #self.structure = get_structure(scn, self.data, self.mats_uv)

        if globs.is_blender_2_79_or_older:
            context.space_data.viewport_shade = 'MATERIAL'        

        self.data = get_data_sable(scn.smc_ob_data)
        self.mats_uv = get_mats_uv(scn, self.data)

        #print(self.sableMaterialMap)
        mapped_materials = get_mapped_materials_sable(scn.smc_ob_data, self.sableMaterialMap)

        for current_category, current_materials in mapped_materials.items(): 
            # Note: current_materials is a Dict with key as a gameobject to a list of materials

            if not current_materials: # is empty, this is totally normal if no materials are in one of this category
                continue

            atlas_name = self.type_to_output_name_sable(scn, current_category)
            create_atlas = self.type_to_create_atlas(scn, current_category)        

            if atlas_name == "":
                if errors:
                    errors += '\n'
                errors += "Atlas " + current_category + " is empty"
                #self.report({'ERROR'}, "Atlas " + current_category + " is empty")
                continue

            structure = get_structure_sable(scn, current_materials, self.mats_uv)
            fittedStructure = BinPacker(get_size_sable(scn, structure)).fit()

            size = get_atlas_size(fittedStructure)
            atlas_size = calculate_adjusted_size(scn, size)

            if max(atlas_size, default=0) > 20000:
                #self.report({'ERROR'}, 'The output image size of {0}x{1}px is too large'.format(*atlas_size))
                if errors:
                    errors += '\n'
                errors += "The output image size of {0}x{1}px is too large'.format(*atlas_size)"
                continue

            atlas = get_atlas_sable(scn, fittedStructure, atlas_size)
            align_uvs_sable(scn, fittedStructure, atlas_name, atlas.size, size)
            atlas_material = create_atlas_material_sable(scn, atlas, self.mats_uv, atlas_name, create_atlas)
            assign_atlased_material_sable(scn, current_materials, atlas_material)

            #self.report({'INFO'}, 'Merged ' + current_category + ' materials and created ' + atlas_name + '!')
            print('Merged ' + current_category + ' materials and created ' + atlas_name + '!')

        clear_mats(scn, self.mats_uv)
        bpy.ops.smc.refresh_ob_data()

        if errors:
            self.report({'ERROR'}, errors)
        else:
            self.report({'INFO'}, 'Atlases Created!')

        return {'FINISHED'}
###