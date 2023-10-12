__all__ = (
    "Animator",
    "AnimKey",
)

from typing import Any, Dict, List, Optional, Sequence

import bpy
import numpy as np


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

    def __init__(self, obj: bpy.types.Object, data_path: str, index: int = 0,
            action_name: Optional[str] = None):
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

    def animate(self, frame: float, value: Any, handle: str = "AUTO_CLAMPED", type: str = "KEYFRAME"):
        """
        Insert keyframe.
        """
        key = self._fcurve.keyframe_points.insert(frame, value)
        key.handle_right_type = handle
        key.handle_left_type = handle
        key.type = type

        self._fcurve.update()


class AnimKey:
    """
    Set of value presets for animators.

    Each key is a list of values corresponding to each animator. The basis
    key is always defined at initialize. Other keys are diffs with respect to
    the basis key.

    Animation is done by assigning weights to each key.

    Usage example:

    .. code-block:: python

       anim1 = bmusic.Animator(obj, "location", 0)
       anim2 = bmusic.Animator(obj, "location", 1)
       anim3 = bmusic.Animator(obj, "location", 2)

       key = bmusic.AnimKey([anim1, anim2, anim3], [0, 0, 0])
       key["up"] = (0, 0, 1)
       key["cool"] = (1, 1, -1)
       key.animate(0)
       key.animate(30, up=2, handle="VECTOR", type="JITTER")
       key.animate(60, up=1, cool=2, type="EXTREME")
    """

    _animators: List[Animator]
    _keys: Dict[str, np.ndarray]

    def __init__(self, animators: List[Animator], basis: Sequence[float]):
        self._animators = animators
        self._keys = {}
        self._keys["basis"] = np.array(basis)

    def __iter__(self):
        return iter(self._keys)

    def __getitem__(self, key: str) -> np.ndarray:
        return self._keys[key]

    def __setitem__(self, key: str, value: Sequence[float]):
        """
        Key is converted to a difference with respect to basis
        i.e. (value - basis)
        """
        assert key not in ("basis", "handle", "type", "frame")
        assert len(value) == len(self._animators)
        value = np.array(value) - self["basis"]
        self._keys[key] = value

    def __delitem__(self, key: str):
        del self._keys[key]

    def __contains__(self, key: str):
        return key in self._keys

    def __len__(self):
        return len(self._keys)

    def __call__(self, *args, **kwargs):
        """
        Same as self.animate(...)
        Included for brevity.
        """
        return self.animate(*args, **kwargs)

    def animate(self, frame: float, handle: str = "AUTO_CLAMPED", type: str = "KEYFRAME",
            **kwargs):
        """
        Animate all animators.

        :param kwargs: Weight of each shape key.
        """
        value = self["basis"]
        for key, weight in kwargs.items():
            value = value + self[key]*weight

        for i, anim in enumerate(self._animators):
            anim.animate(frame, value[i], handle=handle, type=type)
