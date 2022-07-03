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

    animkey: Animation key with following keys:
        - basis: Resting (intensity 0) position.
        - on: Playing (intensity 1) position.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animkey = kwargs.get("animkey")


class IntensityOnOff(Intensity):
    """
    Turns on when a note starts and off when it ends.

    Parameters
    ----------

    duration: Time, in seconds, to spend interpolating from states.
        Default: 0.1

    vector_handles: Whether to use vector handles (no easing in or out).
        Default: False
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

            # Initial resting position
            if i == 0 or note.start-last > 2*duration:
                keys.append((note.start-duration, 0, "JITTER"))

            # Playing through note
            keys.append((note.start, 1, "MOVING_HOLD"))
            keys.append((note.end, 1, "MOVING_HOLD"))

            # Resting after note (sooner if next note close).
            frame = min(note.end+duration, (note.end+next)/2)
            keys.append((frame, 0, "JITTER"))

            for frame, value, type in keys:
                self.animkey.animate(frame, handle=handle, type=type, on=value)
