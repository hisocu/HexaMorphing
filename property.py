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


class HMValues(bpy.types.PropertyGroup):
    use_dir_obj = bpy.props.BoolProperty()
    dir_obj_name = bpy.props.StringProperty()

    x = bpy.props.FloatProperty(min=-1, max=1)
    y = bpy.props.FloatProperty(min=-1, max=1)
    z = bpy.props.FloatProperty(min=-1, max=1)


class HMParam(bpy.types.PropertyGroup):
    bases = bpy.props.PointerProperty(type=HMBases)
    values = bpy.props.PointerProperty(type=HMValues)
    enable = bpy.props.BoolProperty()
