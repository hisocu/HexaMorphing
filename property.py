import bpy


class TMControl(bpy.types.PropertyGroup):
    running = bpy.props.BoolProperty()
    rendering_only = bpy.props.BoolProperty(default=True)
    interval = bpy.props.FloatProperty(min=1. / 60., default=0.1, step=1, precision=3)


class TMVertex(bpy.types.PropertyGroup):
    co = bpy.props.FloatVectorProperty(subtype='XYZ')


class TMBase(bpy.types.PropertyGroup):
    vertices = bpy.props.CollectionProperty(type=TMVertex)


class TMBases(bpy.types.PropertyGroup):
    x = bpy.props.PointerProperty(type=TMBase)
    y = bpy.props.PointerProperty(type=TMBase)
    z = bpy.props.PointerProperty(type=TMBase)


class IntVal(bpy.types.PropertyGroup):
    val = bpy.props.IntProperty()


class IntCollection(bpy.types.PropertyGroup):
    data = bpy.props.CollectionProperty(type=IntVal)


class TMParam(bpy.types.PropertyGroup):
    enable = bpy.props.BoolProperty()

    bases = bpy.props.PointerProperty(type=TMBases)
    dir_obj_name = bpy.props.StringProperty()

    reversible = bpy.props.EnumProperty(items=[('n', 'N', '', 0), ('x', 'X', '', 1), ('y', 'Y', '', 2), ('z', 'Z', '', 3)])
    reference = bpy.props.EnumProperty(items=[('x', 'X', '', 1), ('y', 'Y', '', 2), ('z', 'Z', '', 3)])
