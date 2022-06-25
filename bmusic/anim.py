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

    .. code-block:: python

       anim = Animator(obj, "location", length=3)
       anim.animate(0, (0, 0, 0), handle="AUTO_CLAMPED")
       anim.animate(60, (1, 1, 1), handle="VECTOR")
       anim.animate(120, (2, 2, 2), type="EXTREME")
       anim.animate(180, (3, 3, 3), handle="VECTOR", type="JITTER")

       anim.animate(240, 4, index=1)   # Index 1 (Y) location
    """

    obj: bpy.types.Object
    """Blender object to animate."""
    length: int
    """If a vector property (e.g. location), how many elements in the vector."""

    def __init__(self, obj: bpy.types.Object, data_path: str, length: int = 1,
            action_name: str = None):
        """
        :param action_name: Creates new action for obj with this name if not already present.
            Default obj.action
        """
        self.obj = obj
        self.length = length

        if obj.animation_data is None:
            obj.animation_data_create()
        if obj.animation_data.action is None:
            name = action_name if action_name is not None else f"{obj.name}.action"
            obj.animation_data.action = bpy.data.actions.new(name)

        self._fcurves = []
        for index in range(length):
            if obj.animation_data.action.fcurves.find(data_path, index=index) is None:
                self._fcurves.append(obj.animation_data.action.fcurves.new(data_path, index=index))

    @property
    def data_path(self):
        return self._fcurves[0].data_path

    def animate(self, frame: int, value: Union[Any, Sequence[Any]], index: int = None,
            handle: str = "AUTO_CLAMPED", type: str = "KEYFRAME"):
        """
        Animate either single index or all indices.
        If single index, pass in one value.
        Else, pass in tuple of values.
        """
        if index is None:
            for i in range(self.length):
                self._anim_index(frame, value[i], i, handle, type)
        else:
            self._anim_index(frame, value, index, handle, type)

    def _anim_index(self, frame, value, index, handle, type):
        key = self._fcurves[index].keyframe_points.insert(frame, value)
        key.handle_right_type = handle
        key.handle_left_type = handle
        key.type = type

        self._fcurves[index].update()
