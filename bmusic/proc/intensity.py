"""
Procedures relating to intensity of something e.g. light, piano key's rotation,
string's vibration, etc.
"""

__all__ = (
    "Intensity",
    "IntensityOnOff",
    "IntensityFade",
)

import bpy
import numpy as np

from .procedure import Procedure


class Intensity(Procedure):
    """
    Base intensity class.

    Max intensity is determined by note velocity.

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

    Keyframe types:
    - JITTER: Resting (intensity = 0).
    - BREAKDOWN: Playing.

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
            last = note.prev_end
            next = note.next_start

            keys = []

            # Initial resting position
            if i == 0 or note.start-last > 2*duration:
                keys.append((note.start-duration, 0, "JITTER"))

            # Playing through note
            intensity = np.interp(note.velocity, [0, 127], [0, 1])
            keys.append((note.start, intensity, "BREAKDOWN"))
            keys.append((note.end, intensity, "BREAKDOWN"))

            # Resting after note (sooner if next note close).
            frame = min(note.end+duration, (note.end+next)/2)
            keys.append((frame, 0, "JITTER"))

            for frame, value, type in keys:
                self.animkey.animate(frame, handle=handle, type=type, on=value)


class IntensityFade(Intensity):
    """
    Turns on when a note starts and fades away.

    Keyframe types:
    - JITTER: Resting (intensity = 0).
    - BREAKDOWN: Fading.
    - EXTREME: Max intensity.

    Parameters
    ----------

    fade_fac: Exponential decay factor in factor/sec.
        Default 0.6

    key_interval: Interval in frames for decay section keyframes. Avoids keyframing
        every frame.
        Default: 10

    off_thres: Threshold for intensity to be considered off.
        Default: 0.01

    note_end: Whether to set intensity to 0 at end of note. If false, the note will
        keep glowing until next play.
        Default: True  (stops when note ends).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fade_fac = kwargs.get("fade_fac", 0.3)
        self.key_interval = kwargs.get("key_interval", 10)
        self.off_thres = kwargs.get("off_thres", 0.01)
        self.note_end = kwargs.get("note_end", True)

    def animate(self):
        fac = self.fade_fac ** (1.0/bpy.context.scene.render.fps)
        interval_fac = fac ** self.key_interval

        # Whether last note ended (intensity reached 0) with enough time to require
        # another keyframe at 0 before next note.
        last_ended = True

        for i, note in enumerate(self.midi):
            last = note.prev_end
            next = note.next_start
            long_pause = next > note.end + 3   # Long between this end and next start
            end_frame = next - 3
            if self.note_end:
                end_frame = min(note.end, end_frame)

            intensity = np.interp(note.velocity, [0, 127], [0, 1])

            # Initial intensity
            if last_ended:
                self.animkey.animate(note.start-1, type="JITTER", on=0)
            self.animkey.animate(note.start, type="EXTREME", on=intensity)

            # Fading
            frame = note.start
            while True:
                intensity *= interval_fac
                next_frame = frame + self.key_interval

                if next_frame > end_frame:
                    final_int = intensity * fac ** (end_frame-frame)
                    self.animkey.animate(end_frame, type="BREAKDOWN", on=final_int)
                    if long_pause:
                        # Need to set to 0
                        self.animkey.animate(end_frame+1, type="JITTER", on=0)
                    break

                if intensity < self.off_thres:
                    self.animkey.animate(next_frame, type="JITTER", on=0)
                    break

                self.animkey.animate(next_frame, type="BREAKDOWN", on=intensity)

                frame = next_frame

            last_ended = long_pause
