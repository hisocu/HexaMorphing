bl_info = {
    'name': 'HexaMorphing',
    'author': 'hisocu',
    'version': (0, 1),
    'blender': (2, 78, 0),
    'location': 'View3D > Tools Panel/Properties Panel',
    'description': 'Hexa Morphing',
    'warning': '',
    'support': 'TESTING',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Object'
}

if "bpy" in locals():
    import imp
    imp.reload(ui)
    imp.reload(property)
    imp.reload(hexa_morph)
    imp.reload(base_operator)
    imp.reload(toggle_morphing)

else:
    from .ui import *
    from .property import *
    from .hexa_morph import *
    from .base_operator import *
    from .toggle_morphing import *

import bpy


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Object.morph_param = bpy.props.PointerProperty(type=HMParam)
    bpy.types.Scene.morph_ctrl = bpy.props.PointerProperty(type=HMControl)


def unregister():
    if hasattr(bpy.types.Object, 'morph_param'):
        del bpy.types.Object.morph_param

    if hasattr(bpy.types.Scene, 'morph_ctrl'):
        del bpy.types.Scene.morph_ctrl

    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
