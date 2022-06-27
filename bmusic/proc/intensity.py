"""
Procedures relating to intensity of something e.g. light, piano key's rotation,
string's vibration, etc.
"""

__all__ = (
    "Intensity",
    "IntensityOnOff",
)

import bpy

from .procedure import Procedure


class Intensity(Procedure):
    """
    Base intensity class.

    Parameters
    ----------

    animators: List of Animator objects corresponding to properties
        to animate.

    min: Minimum intensity for all animators.

    max: Maximum intensity for all animators.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animators = kwargs.get("animators", [])
        self.min = kwargs.get("min", 0)
        self.max = kwargs.get("max", 1)


class IntensityOnOff(Intensity):
    """
    Turns on when a note starts and off when it ends.

    Parameters
    ----------

    duration: Time, in seconds, to spend interpolating from states.

    vector_handles: Whether to use vector handles (no easing in or out).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duration = kwargs.get("duration", 0.1)
        self.vector_handles = kwargs.get("vector_handles", False)

    def animate(self):
        duration = self.duration * bpy.context.scene.render.fps
        handle = "VECTOR" if self.vector_handles else "AUTO_CLAMPED"

        for note in self.midi:
            for anim in self.animators:
                anim.animate(note.start-duration, self.min, handle=handle)
                anim.animate(note.start, self.max, handle=handle)
                anim.animate(note.end, self.max, handle=handle)
                anim.animate(note.end+duration, self.min, handle=handle)
