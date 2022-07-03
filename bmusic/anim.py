__all__ = (
    "Animator",
)

from typing import Any, Sequence, Union

import bpy


class Animator:
    """
    Wrapper around Blender's animation API, providing control of keyframe type and
    handles.

    Usage example:

    .. code-block:: py

       anim = Animator(obj, "location", index=1)   # Y location
       anim.animate(0, 0)
       anim.animate(10, 10, handle="VECTOR")
       anim.animate(20, 20, type="EXTREME")
    """

    obj: bpy.types.Object
    """Blender object to animate."""

    def __init__(self, obj: bpy.types.Object, data_path: str, index: int = 1,
            action_name: str = None):
        """
        :param index: If a vector property, index of the component to animate, e.g. index 1 for Y location.
        :param action_name: Creates new action for obj with this name if not already present.
            Default obj.action
        """
        self.obj = obj
        self.index = index

        if obj.animation_data is None:
            obj.animation_data_create()
        if obj.animation_data.action is None:
            name = action_name if action_name is not None else f"{obj.name}.action"
            obj.animation_data.action = bpy.data.actions.new(name)

        self._fcurve = obj.animation_data.action.fcurves.find(data_path, index=index)
        if self._fcurve is None:
            self._fcurve = obj.animation_data.action.fcurves.new(data_path, index=index)

    @property
    def data_path(self):
        return self._fcurve.data_path

    def animate(self, frame: int, value: Any, handle: str = "AUTO_CLAMPED", type: str = "KEYFRAME"):
        """
        Insert keyframe.
        """
        key = self._fcurve.keyframe_points.insert(frame, value)
        key.handle_right_type = handle
        key.handle_left_type = handle
        key.type = type

        self._fcurve.update()
