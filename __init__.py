bl_info = {
    'name': 'TriMorphing',
    'author': 'hisocu',
    'version': (0, 1),
    'blender': (2, 78, 0),
    'location': 'View3D > Tools Panel/Properties Panel',
    'description': 'Tri Morphing',
    'warning': '',
    'support': 'TESTING',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Object'
}

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(property)
    importlib.reload(tri_morphing)
    importlib.reload(base_operator)
    importlib.reload(morphing_operator)

else:
    from .ui import *
    from .property import *
    from .tri_morphing import *
    from .base_operator import *
    from .morphing_operator import *

import bpy


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Object.morph_param = bpy.props.PointerProperty(type=TMParam)
    bpy.types.Scene.morph_ctrl = bpy.props.PointerProperty(type=TMControl)


def unregister():
    if hasattr(bpy.types.Object, 'morph_param'):
        del bpy.types.Object.morph_param

    if hasattr(bpy.types.Scene, 'morph_ctrl'):
        del bpy.types.Scene.morph_ctrl

    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
