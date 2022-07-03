__all__ = (
    "AnimKey",
)

from typing import Dict, List, Sequence

import numpy as np

from .anim import Animator


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
    _keys: Dict[str, List[float]]

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
