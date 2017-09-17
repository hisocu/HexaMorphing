import bpy
from .morphing_operator import *
from .base_operator import *
from .hexa_morphing import *


class VIEW3D_PT_HMTools(bpy.types.Panel):
    bl_label = 'Hexa Morphing'
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
    bl_label = 'Hexa Morphing'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        for object in bpy.data.objects:
            if object.select and object.type == 'MESH':
                return True
        return False

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.active_object.morph_param, 'enable', text='')

    def draw(self, context):
        def tag_map(e):
            return {'+': 'p', '-': 'm'}[e[0]] + e[1].lower()

        layout = self.layout
        scene = context.scene
        object = context.object
        morphp = object.morph_param

        layout.enabled = morphp.enable

        labels = ['X', 'Y', 'Z']

        opp_flag = usable_opposite(object.data)

        for label in labels:
            box = layout.box()
            row = box.row()

            for lb in [s + label for s in '-+']:
                sub_box = row.box()

                column = sub_box.column(align=True)
                column.label(text=lb + ':')

                col1 = column.column(align=True)
                col1.operator(
                    RegisterBase.bl_idname,
                    text='register base').tag = tag_map(lb)
                col1.operator(
                    CopyBase.bl_idname, text='copy base').tag = tag_map(lb)

                col2 = column.column(align=True)
                col2.prop(getattr(morphp.bases, tag_map(lb)), 'use_opp_side')

                col1.enabled = not getattr(morphp.bases,
                                           tag_map(lb)).use_opp_side
                col2.enabled = opp_flag

            column = box.column(align=True)
            column.prop(morphp.values, label.lower(), text=label)
            column.enabled = not morphp.values.use_dir_obj

        layout.separator()

        column = layout.column(align=True)

        layout.prop(morphp.values, 'use_dir_obj', text='use direction object')
        column = layout.column(align=True)
        column.prop_search(
            morphp.values, 'dir_obj_name', scene, 'objects', text='')
        column.enabled = morphp.values.use_dir_obj
