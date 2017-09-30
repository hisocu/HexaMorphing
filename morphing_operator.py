import bpy
import sys, traceback
import mathutils as mu
from functools import partial
from .tri_morphing import *


def handler(target_handlers, scene):
    try:
        i = 0
        for target in bpy.data.objects:
            morphp = target.morph_param

            if morphp.enable and morphp.dir_obj_name != "":
                dir_obj = bpy.data.objects[morphp.dir_obj_name]
                to_vec = (target.matrix_world * dir_obj.matrix_world.translation) - target.matrix_world.translation
                x, y, z = to_vec

                target_handlers[i % len(target_handlers)]((x, y, z))
                i += 1

                target.data.update()

    except:
        for info in sys.exc_info():
            print(info)
            print(traceback.format_exc())
        return


class ToggleMorphing(bpy.types.Operator):
    bl_idname = 'scene.toggle_morphing'
    bl_label = 'ToggleMorphing'
    bl_description = 'ToggleMorphing'

    def __init__(self):
        self.__timer = None
        self.__handler = None

    def __add_timer_handler(self, context):
        morphc = context.scene.morph_ctrl

        if self.__timer is None:
            self.__timer = context.window_manager.event_timer_add(morphc.interval, context.window)
            context.window_manager.modal_handler_add(self)

    def __remove_timer_handler(self, context):
        if self.__timer is not None:
            context.window_manager.event_timer_remove(self.__timer)
            self.__timer = None

    def __add_app_handler(self, context):
        bpy.app.handlers.frame_change_post.append(self.__handler)

    def __remove_app_handler(self, context):
        while self.__handler in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(self.__handler)

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

        self.__handler(context.scene)

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

                target_handlers = []

                for target in bpy.data.objects:
                    morphp = target.morph_param

                    if morphp.enable and is_opposite_loop_mappable(target.data):
                        bases = list(map(partial(getattr, morphp.bases), 'xyz')) * 2
                        reference_axis = {'x': 0, 'y': 1, 'z': 2}[morphp.reference]

                        front_vgetters, back_vgetters = gen_fb_vertex_getters(target.data, bases, reference_axis)

                        target_handlers.append(partial(tri_morph, target.data, front_vgetters, back_vgetters, reference_axis))

                self.__handler = partial(handler, target_handlers)

                return {'RUNNING_MODAL'}

        else:
            return {'CANCELLED'}
