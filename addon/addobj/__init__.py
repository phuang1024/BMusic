"""
Add object(s) submodule.
"""

import bpy

from .add_string import BMUSIC_OT_AddString


class BasePanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BMusic"
    bl_options = {"DEFAULT_CLOSED"}


class BMUSIC_PT_AddObj(BasePanel, bpy.types.Panel):
    bl_label = "Add Object"
    bl_idname = "BMUSIC_PT_AddObj"

    def draw(self, context):
        layout = self.layout

        layout.operator("bmusic.add_string", icon="IPO_ELASTIC")


classes = (
    BMUSIC_PT_AddObj,

    BMUSIC_OT_AddString,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
