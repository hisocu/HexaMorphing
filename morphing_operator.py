import bpy
import sys
from .hexa_morphing import *


def handler(scene):
    try:
        for target in bpy.data.objects:
            if target.morph_param.enable:
                morphp = target.morph_param
                dir_obj = bpy.data.objects[morphp.values.dir_obj_name]
                to_vec = (target.matrix_world * dir_obj.matrix_world.
                          translation) - target.matrix_world.translation
                x, y, z = to_vec

                bases = [
                    getattr(morphp.bases, s + a) for s in 'pm' for a in 'xyz'
                ]
                opp_flags = [
                    usable_opposite(target.data) and base.use_opp_side
                    for base in bases
                ]
                bases = [
                    target.data
                    if not opp_flag and len(base.vertices) == 0 else base
                    for base, opp_flag in zip(bases, opp_flags)
                ]

                hexa_morph(target.data, bases, (x, y, z), opp_flags)

                target.data.update()

            if bpy.context.area:
                bpy.context.area.tag_redraw()

    except:
        for info in sys.exc_info():
            print(info)
        return


class ToggleMorphing(bpy.types.Operator):
    bl_idname = 'scene.toggle_morphing'
    bl_label = 'ToggleMorphing'
    bl_description = 'ToggleMorphing'

    def __init__(self):
        self.__timer = None

    def __add_timer_handler(self, context):
        morphc = context.scene.morph_ctrl

        if self.__timer is None:
            self.__timer = context.window_manager.event_timer_add(
                morphc.interval, context.window)
            context.window_manager.modal_handler_add(self)

    def __remove_timer_handler(self, context):
        if self.__timer is not None:
            context.window_manager.event_timer_remove(self.__timer)
            self.__timer = None

    def __add_app_handler(self, context):
        bpy.app.handlers.frame_change_post.append(handler)

    def __remove_app_handler(self, context):
        for handle in bpy.app.handlers.scene_update_post:
            if handle.__name__ == 'handler':
                bpy.app.handlers.frame_change_post.remove(handle)

                break

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        morphc = context.scene.morph_ctrl

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        if context.area:
            context.area.tag_redraw()

        if not morphc.running:
            self.__remove_timer_handler(context)

            return {'FINISHED'}

        handler(context.scene)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        morphc = context.scene.morph_ctrl

        if context.area.type == 'VIEW_3D':
            if morphc.running:
                self.__remove_app_handler(context)

                morphc.running = False

                return {'FINISHED'}

            else:
                self.__add_app_handler(context)

                if not morphc.rendering_only:
                    self.__add_timer_handler(context)

                morphc.running = True

                return {'RUNNING_MODAL'}

        else:
            return {'CANCELLED'}
