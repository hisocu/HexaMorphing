import bpy

tag_enum_items = [("px", "+X", "", 0), ("py", "+Y", "", 1),
                  ("pz", "+Z", "", 2), ("mx", "-X", "", 3),
                  ("my", "-Y", "", 4), ("mz", "-Z", "", 5)]


class RegisterBase(bpy.types.Operator):
    bl_idname = "object.register_base"
    bl_label = "RegisterBase"
    bl_description = "RegisterBase"
    bl_options = {'REGISTER', 'UNDO'}

    tag = bpy.props.EnumProperty(items=tag_enum_items)

    def execute(self, context):
        src = context.object.data.vertices
        dst = getattr(context.object.morph_param.bases, self.tag).vertices

        dst.clear()

        for s in src:
            d = dst.add()
            d.co.x = s.co.x
            d.co.y = s.co.y
            d.co.z = s.co.z

        return {'FINISHED'}


class CopyBase(bpy.types.Operator):
    bl_idname = "object.copy_base"
    bl_label = "CopyBase"
    bl_description = "CopyBase"
    bl_options = {'REGISTER', 'UNDO'}

    tag = bpy.props.EnumProperty(items=tag_enum_items)

    def execute(self, context):
        src = getattr(context.object.morph_param.bases, self.tag).vertices
        dst = context.object.data.vertices

        for s, d in zip(src, dst):
            d.co.x = s.co.x
            d.co.y = s.co.y
            d.co.z = s.co.z

        return {'FINISHED'}
