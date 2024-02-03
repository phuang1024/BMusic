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

import bpy


class VIEW3D_MT_AddBmusic(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_AddBmusic"
    bl_label = "BMusic"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_REGION_WIN"


def draw_bmusic_menu(self, context):
    layout = self.layout
    layout.operator_context = "INVOKE_REGION_WIN"

    layout.separator()
    layout.menu("VIEW3D_MT_mesh_vert_add", icon="DECORATE")


classes = (
    VIEW3D_MT_AddBmusic,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_mesh_add.append(draw_bmusic_menu)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_mesh_add.remove(draw_bmusic_menu)
