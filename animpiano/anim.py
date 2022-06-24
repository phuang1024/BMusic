from typing import Any, Sequence, Union

import bpy


class Animator:
    """
    Wrapper around Blender's animation API, providing control of keyframe type and
    handles.
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

        anim = self.obj.animation_data
        if anim is None:
            anim_create()
        if anim.action is None:
            name = action_name if action_name is not None else f"{obj.name}.action"
            anim.action = bpy.data.actions.new(name)

        self._fcurves = []
        for index in range(length):
            if anim.action.fcurves.find(data_path, index=index) is None:
                self._fcurves.append(anim.action.fcurves.new(data_path, index=index))

    @property
    def data_path(self):
        return self._fcurves[0].data_path

    def animate(self, frame: int, value: Union[Any, Sequence[Any]], index: int = None):
        """
        Animate either single index or all indices.
        If single index, pass in one value.
        Else, pass in tuple of values.
        """
        if index is None:
            for i in range(self.length):
                self._anim_index(frame, value[i], i)
        else:
            self._anim_index(frame, value, index)

    def _anim_index(self, frame, value, index):
        self._fcurves[index].keyframe_points.insert(frame, value)
