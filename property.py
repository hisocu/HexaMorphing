import bpy


class HMControl(bpy.types.PropertyGroup):
    running = bpy.props.BoolProperty()
    rendering_only = bpy.props.BoolProperty(default=True)
    interval = bpy.props.FloatProperty(
        min=1. / 60., default=0.1, step=1, precision=3)


class HMVertex(bpy.types.PropertyGroup):
    co = bpy.props.FloatVectorProperty(subtype='XYZ')


class HMBase(bpy.types.PropertyGroup):
    use_opp_side = bpy.props.BoolProperty()
    vertices = bpy.props.CollectionProperty(type=HMVertex)


class HMBases(bpy.types.PropertyGroup):
    px = bpy.props.PointerProperty(type=HMBase)
    mx = bpy.props.PointerProperty(type=HMBase)
    py = bpy.props.PointerProperty(type=HMBase)
    my = bpy.props.PointerProperty(type=HMBase)
    pz = bpy.props.PointerProperty(type=HMBase)
    mz = bpy.props.PointerProperty(type=HMBase)


class HMParam(bpy.types.PropertyGroup):
    enable = bpy.props.BoolProperty()

    bases = bpy.props.PointerProperty(type=HMBases)
    dir_obj_name = bpy.props.StringProperty()

    reversible = bpy.props.EnumProperty(
        items=[('n', 'N', '', 0),
               ('x', 'X', '', 1), ('y', 'Y', '', 2), ('z', 'Z', '', 3)])
