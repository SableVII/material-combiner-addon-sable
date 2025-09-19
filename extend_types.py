import bpy
from bpy.props import *

from . import addon_updater_ops


class CombineList(bpy.types.PropertyGroup):
    ob = PointerProperty(
        name='Current Object',
        type=bpy.types.Object,
    )
    ob_id = IntProperty(default=0)
    mat = PointerProperty(
        name='Current Object Material',
        type=bpy.types.Material,
    )
    layer = IntProperty(
        name='Material Layers',
        description='Materials with the same number will be merged together.'
                    '\nUse this to create multiple materials linked to the same atlas file',
        min=1,
        max=99,
        step=1,
        default=1,
    )
    used = BoolProperty(default=True)
    type = IntProperty(default=0)


class UpdatePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    auto_check_update = BoolProperty(
        name='Auto-check for Update',
        description='If enabled, auto-check for updates using an interval',
        default=True,
    )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description='Number of months between checking for updates',
        default=0,
        min=0
    )
    updater_intrval_days = IntProperty(
        name='Days',
        description='Number of days between checking for updates',
        default=1,
        min=1
    )
    updater_intrval_hours = IntProperty(
        name='Hours',
        description='Number of hours between checking for updates',
        default=0,
        min=0,
        max=0
    )
    updater_intrval_minutes = IntProperty(
        name='Minutes',
        description='Number of minutes between checking for updates',
        default=0,
        min=0,
        max=0
    )

    def draw(self, context: bpy.types.Context):
        addon_updater_ops.update_settings_ui(self, context)


def register() -> None:
    bpy.types.Scene.smc_ob_data = CollectionProperty(type=CombineList)
    bpy.types.Scene.smc_ob_data_id = IntProperty(default=0)
    bpy.types.Scene.smc_list_id = IntProperty(default=0)
    bpy.types.Scene.smc_size = EnumProperty(
        name='Atlas size',
        items=[
            ('PO2', 'Power of 2', 'Combined image size is power of 2'),
            ('QUAD', 'Quadratic', 'Combined image has same width and height'),
            ('AUTO', 'Automatic', 'Combined image has minimal size'),
            ('CUST', 'Custom', 'Combined image has proportionally scaled to fit in custom size'),
            ('STRICTCUST', 'Strict Custom', 'Combined image has exact custom width and height'),
        ],
        description='Select atlas size',
        default='QUAD',
    )
    bpy.types.Scene.smc_size_width = IntProperty(
        name='Max width (px)',
        description='Select max width for combined image',
        min=8,
        max=8192,
        step=1,
        default=4096,
    )
    bpy.types.Scene.smc_size_height = IntProperty(
        name='Max height (px)',
        description='Select max height for combined image',
        min=8,
        max=8192,
        step=1,
        default=4096,
    )
    bpy.types.Scene.smc_crop = BoolProperty(
        name='Crop outside images by UV',
        description='Crop images by UV if materials UV outside of bounds',
        default=True,
    )
    bpy.types.Scene.smc_pixel_art = BoolProperty(
        name='Pixel Art / Small Textures',
        description='Avoids 1-pixel UV scaling for small textures.'
                    '\nDisable for larger textures to avoid blending with nearby pixels',
        default=False,
    )
    bpy.types.Scene.smc_diffuse_size = IntProperty(
        name='Size of materials without image',
        description='Select the size of materials that only consist of a color',
        min=8,
        max=256,
        step=1,
        default=32,
    )
    bpy.types.Scene.smc_gaps = IntProperty(
        name='Size of gaps between images',
        description='Select size of gaps between images',
        min=0,
        max=32,
        step=200,
        default=0,
        options={'HIDDEN'},
    )
    bpy.types.Scene.smc_save_path = StringProperty(
        description='Select the directory in which the generated texture atlas will be saved',
        default='',
    )

    ### Sable Tweaks
    bpy.types.Scene.smc_sable_outfit_texture_name = StringProperty(
        description='The name of the generated Outfit texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_outfit_texture = BoolProperty(
        name='Create Outfit Texture',
        description='Create Outfit atlased texture',
        default=False,
    )        
    bpy.types.Scene.smc_sable_body_texture_name = StringProperty(
        description='The name of the generated Body atlased texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_body_texture = BoolProperty(
        name='Create Body Texture',
        description='Create Body atlased texture',
        default=False,
    )
    bpy.types.Scene.smc_sable_hair_texture_name = StringProperty(
        description='The name of the generated Hair atlased texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_hair_texture = BoolProperty(
        name='Create Hair Texture',
        description='Create Hair atlased texture',
        default=False,
    )
    bpy.types.Scene.smc_sable_eyereflections_texture_name = StringProperty(
        description='The name of the generated Eye Reflections atlased texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_eyereflections_texture = BoolProperty(
        name='Create Eye Reflections Texture',
        description='Create Eye Reflections atlased texture',
        default=False,
    )
    bpy.types.Scene.smc_sable_emissives_texture_name = StringProperty(
        description='The name of the generated Emissives atlased texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_emissives_texture = BoolProperty(
        name='Create Emissives Texture',
        description='Create Emissives atlased texture',
        default=False,
    )
    bpy.types.Scene.smc_sable_transparents_texture_name = StringProperty(
        description='The name of the generated Transparents atlased texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_transparents_texture = BoolProperty(
        name='Create Transparents Texture',
        description='Create Transparents atlased texture',
        default=False,
    )
    bpy.types.Scene.smc_sable_eyes_texture_name = StringProperty(
        description='The name of the generated Eyes atlased texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_eyes_texture = BoolProperty(
        name='Create Eyes Texture',
        description='Create Eyes atlased texture',
        default=False,
    )
    bpy.types.Scene.smc_sable_HUDelements_texture_name = StringProperty(
        description='The name of the generated HUD Elements atlased texture',
        default='',
    )
    bpy.types.Scene.smc_sable_create_HUDelements_texture = BoolProperty(
        name='Create HUD Elements Texture',
        description='Create HUD Elements atlased texture',
        default=False,
    ) 

    bpy.types.Scene.smc_sable_merge_by_distance_weight = FloatProperty(
        name='Merge by Distance Weight',
        description='Merge by Distance Weight. Set to 0 if no merging is wanted',
        default=0.00005,
    )
    ###

    bpy.types.Material.root_mat = PointerProperty(
        name='Material Root',
        type=bpy.types.Material,
    )
    bpy.types.Material.smc_diffuse = BoolProperty(
        name='Multiply image with diffuse color',
        description='Multiply the materials image with its diffuse color.'
                    '\nINFO: If this color is white the final image will be the same',
        default=True,
    )
    bpy.types.Material.smc_size = BoolProperty(
        name='Custom image size',
        description='Select the max size for this materials image in the texture atlas',
        default=False,
    )
    bpy.types.Material.smc_size_width = IntProperty(
        name='Max width (px)',
        description='Select max width for material image',
        min=8,
        max=8192,
        step=1,
        default=2048,
    )
    bpy.types.Material.smc_size_height = IntProperty(
        name='Max height (px)',
        description='Select max height for material image',
        min=8,
        max=8192,
        step=1,
        default=2048,
    )


def unregister() -> None:
    del bpy.types.Scene.smc_ob_data
    del bpy.types.Scene.smc_ob_data_id
    del bpy.types.Scene.smc_list_id
    del bpy.types.Scene.smc_size
    del bpy.types.Scene.smc_size_width
    del bpy.types.Scene.smc_size_height
    del bpy.types.Scene.smc_crop
    del bpy.types.Scene.smc_pixel_art
    del bpy.types.Scene.smc_diffuse_size
    del bpy.types.Scene.smc_gaps
    del bpy.types.Scene.smc_save_path

    ### Sable Tweaks
    del bpy.types.Scene.smc_sable_outfit_texture_name
    del bpy.types.Scene.smc_sable_body_texture_name
    del bpy.types.Scene.smc_sable_hair_texture_name
    del bpy.types.Scene.smc_sable_eyereflections_texture_name    
    del bpy.types.Scene.smc_sable_emissives_texture_name
    del bpy.types.Scene.smc_sable_transparents_texture_name
    del bpy.types.Scene.smc_sable_create_outfit_texture
    del bpy.types.Scene.smc_sable_create_body_texture
    del bpy.types.Scene.smc_sable_create_hair_texture
    del bpy.types.Scene.smc_sable_create_eyereflections_texture    
    del bpy.types.Scene.smc_sable_create_emissives_texture
    del bpy.types.Scene.smc_sable_create_transparents_texture    

    del bpy.types.Scene.smc_sable_merge_by_distance_weight
    ###

    del bpy.types.Material.root_mat
    del bpy.types.Material.smc_diffuse
    del bpy.types.Material.smc_size
    del bpy.types.Material.smc_size_width
    del bpy.types.Material.smc_size_height
