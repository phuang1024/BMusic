"""
Add string operator.
"""

import bpy
from bpy.props import *


class BMUSIC_OT_AddString(bpy.types.Operator):
    bl_idname = "bmusic.add_string"
    bl_label = "Add String"
    bl_options = {"REGISTER", "UNDO"}

    obj_name: StringProperty(
        name="Object Name",
        default="String",
    )

    length: FloatProperty(
        name="Length",
        default=1.0,
    )

    def execute(self, context):
        add_string_main(self, context)
        return {"FINISHED"}


def add_string_main(self, context):
    name = self.obj_name

    curve = bpy.data.curves.new(name=f"{name}.curve", type="CURVE")
    curve.dimensions = "3D"
    sp = curve.splines.new("NURBS")
    sp.use_endpoint_u = True
    sp.points.add(3)   # Total 4 points
    sp.order_u = 5
    for i in range(4):
        sp.points[i].co = (i/4 * self.length, 0, 0, 1)
    obj_curve = bpy.data.objects.new(f"{name}.curve", curve)
    context.collection.objects.link(obj_curve)

