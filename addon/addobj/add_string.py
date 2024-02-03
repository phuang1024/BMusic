"""
Add string operator.
"""

import bpy


class BMUSIC_OT_AddString(bpy.types.Operator):
    bl_idname = "bmusic.add_string"
    bl_label = "Add String"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.report({"WARNING"}, "Not implemented yet")
        return {"FINISHED"}
