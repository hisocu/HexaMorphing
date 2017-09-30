import bpy
from .morphing_operator import *
from .base_operator import *
from .tri_morphing import *


class VIEW3D_PT_HMTools(bpy.types.Panel):
    bl_label = 'Tri Morphing'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = bl_label

    def draw(self, context):
        layout = self.layout
        morphc = context.scene.morph_ctrl

        col1 = layout.column()
        col1.prop(morphc, 'rendering_only')
        col1.enabled = not morphc.running

        col2 = layout.column()
        col2.prop(morphc, 'interval')
        col2.enabled = not (morphc.running or morphc.rendering_only)

        if morphc.running:
            layout.operator(ToggleMorphing.bl_idname, text='disable morphing')

        else:
            layout.operator(ToggleMorphing.bl_idname, text='enable morphing')


class VIEW3D_PT_HMProps(bpy.types.Panel):
    bl_label = 'Tri Morphing'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        for object in bpy.data.objects:
            if object.select and object.type == 'MESH' and is_opposite_loop_mappable(object.data):
                return True
        return False

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.active_object.morph_param, 'enable', text='')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = context.object
        morphp = object.morph_param

        layout.enabled = morphp.enable

        column = layout.column(align=True)
        column.label(text='direction object:')
        column.prop_search(morphp, 'dir_obj_name', scene, 'objects', text='')

        layout.separator()

        labels = 'XYZ'

        opp_flag = is_opposite_loop_mappable(object.data)
        box = layout.box()

        for label in labels:
            row = box.row()
            sub_box = row.box()

            column = sub_box.column(align=True)
            column.label(text=label + ':')

            column = column.column(align=True)
            column.operator(RegisterBase.bl_idname, text='register base').tag = label.lower()
            column.operator(CopyBase.bl_idname, text='copy base').tag = label.lower()

        layout.separator()

        column = layout.column(align=True)
        column.prop(morphp, 'reversible')
        column.prop(morphp, 'reference')
