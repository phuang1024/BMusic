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

        for i, note in enumerate(self.midi):
            last = note.prev.end if note.prev else -1e9
            next = note.next.start if note.next else 1e9

            keys = []
            if i == 0 or note.start-last > 2*duration:
                keys.append((note.start-duration, self.min))
            keys.append((note.start, self.max))
            keys.append((note.end, self.min))
            frame = min(note.end+duration, (note.end+next)/2)
            keys.append((frame, self.min))

            for anim in self.animators:
                for frame, value in keys:
                    anim.animate(frame, value, handle=handle)
