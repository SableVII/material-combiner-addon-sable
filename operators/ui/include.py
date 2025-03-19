import bpy

from ... import globs
from ...icons import get_icon_id
from ...type_annotations import Scene
from ...ui.main_menu import MaterialMenu


def draw_ui(context: bpy.types.Context, m_col: bpy.types.UILayout) -> None:
    if globs.pil_exist:
        _materials_list(context.scene, m_col)
    elif globs.smc_pi:
        col = m_col.box().column()
        col.label(text='Installation complete', icon_value=get_icon_id('done'))
        col.label(text='Please restart Blender', icon_value=get_icon_id('null'))
    else:
        MaterialMenu.pillow_installator(m_col)


def _materials_list(scn: Scene, m_col: bpy.types.UILayout) -> None:
    patreon = 'https://www.patreon.com/shotariya'
    buymeacoffee = 'https://buymeacoffee.com/shotariya'

    if scn.smc_ob_data:
        m_col.template_list('SMC_UL_Combine_List', 'combine_list', scn, 'smc_ob_data',
                            scn, 'smc_ob_data_id', rows=12, type='DEFAULT')
    col = m_col.column(align=True)
    col.scale_y = 1.2
    col.operator('smc.refresh_ob_data',
                 text='Update Material List' if scn.smc_ob_data else 'Generate Material List',
                 icon_value=get_icon_id('null'))
    col = m_col.column()
    col.scale_y = 1.5
    col.operator('smc.combiner', text='Save Atlas to..', icon_value=get_icon_id('null')).cats = True
    col.separator()
    ### Sable Tweaks
    col.operator('smc.combiner_sable', text='Generate Sable Atlas', icon_value=get_icon_id('null'))
    col = m_col.column()
    col.label(text='Outfit Texture Name')
    col.prop(scn, 'smc_sable_outfit_texture_name', text='')
    col.prop(scn, 'smc_sable_create_outfit_texture')
    col.separator()
    col.label(text='Body Texture Name')
    col.prop(scn, 'smc_sable_body_texture_name', text='')
    col.prop(scn, 'smc_sable_create_body_texture')
    col.separator()
    col.label(text='Hair Texture Name')
    col.prop(scn, 'smc_sable_hair_texture_name', text='')
    col.prop(scn, 'smc_sable_create_hair_texture')
    col.separator()
    col.label(text='Eyes Texture Name')
    col.prop(scn, 'smc_sable_eyes_texture_name', text='')
    col.prop(scn, 'smc_sable_create_eyes_texture')
    col.separator()
    col.label(text='Emissive Texture Name')
    col.prop(scn, 'smc_sable_emissive_texture_name', text='')
    col.prop(scn, 'smc_sable_create_emissive_texture')
    col.separator()
    col.label(text='Transparents Texture Name')
    col.prop(scn, 'smc_sable_transparents_texture_name', text='')
    col.prop(scn, 'smc_sable_create_transparents_texture')
    col.separator()        
    col.prop(scn, 'smc_sable_merge_by_distance_weight', text='Merge by Distance')    
    col.separator()
    ###
    col = m_col.column()
    col.label(text='If this saved you time:')
    col.operator('smc.browser', text='Support Material Combiner', icon_value=get_icon_id('patreon')).link = patreon
    col.operator('smc.browser', text='Buy Me a Coffee', icon_value=get_icon_id('bmc')).link = buymeacoffee
