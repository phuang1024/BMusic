bl_info = {
    "name": "BMusic",
    "description": "Tools for procedural music animation",
    "author": "Patrick Huang",
    "version": (0, 1, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "https://github.com/phuang1024/BMusic",
    "tracker_url": "https://github.com/phuang1024/BMusic/issues",
    "category": "3D View",
}

from . import addobj


def register():
    addobj.register()

def unregister():
    addobj.unregister()
