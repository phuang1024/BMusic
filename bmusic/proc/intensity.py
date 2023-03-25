"""
Procedures relating to intensity of something.
e.g. light, piano key's depression, string's vibration, etc.
"""

__all__ = (
    "Intensity",
    "IntensityOnOff",
    "IntensityFade",
    "IntensityWobble",
)

import bpy
import numpy as np

from ..anim import *
from ..midi import *
from ..utils import *
from .procedure import Procedure


class Intensity(Procedure):
    """
    Base intensity class.

    :Parameters:

        - animkey: Animation key with following keys:

          - basis: Resting (intensity 0) position.
          - on: Playing (intensity max) position.

        - use_velocity: Whether to scale peak intensity based on
          message velocity.

          - Default: True
    """

    animkey: AnimKey
    use_velocity: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animkey = kwargs.get("animkey")
        self.use_velocity = kwargs.get("use_velocity", True)

    def get_intensity(self, msg: Message):
        """
        Returns either msg.velocity/127 or 1 depending on self.use_velocity
        """
        if self.use_velocity:
            return msg.velocity / 127
        else:
            return 1


class IntensityOnOff(Intensity):
    """
    Turns on when a note starts and off when it ends.

    :Keyframe types:

        - JITTER: Resting (intensity = 0).
        - BREAKDOWN: Playing.

    :Parameters:

        - duration: Time, in seconds, to spend interpolating between states.

          - Default: 0.1

        - vector_handles: Whether to use vector handles (no easing in or out).

          - Default: False
    """

    duration: float
    vector_handles: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duration = kwargs.get("duration", 0.1)
        self.vector_handles = kwargs.get("vector_handles", False)

    def animate(self):
        duration = self.duration * bpy.context.scene.render.fps
        handle = "VECTOR" if self.vector_handles else "AUTO_CLAMPED"

        msgs = compute_affixes(self.midi, max_prefix=duration, max_suffix=duration, suffix_after_end=True)
        for msg in msgs:
            intensity = self.get_intensity(msg)

            # For brevity, make a list and call func later.
            # List of (frame, value, key_type)
            keys = []

            # Initial resting position
            keys.append((msg.start-msg.prefix, 0, "JITTER"))
            # Playing through note
            keys.append((msg.start, intensity, "BREAKDOWN"))
            keys.append((msg.end, intensity, "BREAKDOWN"))
            # Resting after note
            if msg.suffix >= duration:
                # Only if suffix is full length; otherwise, the next note will take care of it.
                keys.append((msg.end+msg.suffix, 0, "JITTER"))

            for frame, value, type in keys:
                self.animkey.animate(frame, handle=handle, type=type, on=value)


class IntensityFade(Intensity):
    """
    Turns on when a note starts and fades away.

    :Keyframe types:

        - JITTER: Resting (intensity = 0).
        - BREAKDOWN: Fading.
        - EXTREME: Max intensity.

    :Parameters:

        - fade_func: Function that curves linear time to fade intensity.
          Takes parameters ``(t,)`` (time in seconds since note start) and returns
          between 0 and 1, where 0 is off and 1 is max intensity. There are a few
          predefined functions in this class.

          - Default ``EXPONENTIAL(0.6)`` (exponential decay at 0.6/sec)

        - start_time: Time, in seconds, from off to initial on.

          - Default: 0.1

        - key_interval: Interval in seconds for decay keyframes. Avoids unneccessary
          keyframing on every frame.

          - Default: 0.3

        - off_thres: Threshold for intensity to be considered off. Keyframing will stop
          at this point. If using a custom ``fade_func`` that is NOT monotonically decreasing,
          set this to ``0``.

          - Default: 0.001

        - max_len: Maximum length of note, in seconds. Keyframing will stop after this
          time, even if the note is still playing.

          - Default: 60

        - note_end: Whether to cut intensity to 0 at end of note. If false, the note will
          keep fading until next play, even if the note was released.

          - Default: True  (stops when note ends).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fade_func = kwargs.get("fade_func", self.EXPONENTIAL(0.6))
        self.start_time = kwargs.get("start_time", 0.1)
        self.key_interval = kwargs.get("key_interval", 0.3)
        self.off_thres = kwargs.get("off_thres", 0.001)
        self.max_len = kwargs.get("max_len", 60)
        self.note_end = kwargs.get("note_end", True)

    def animate(self):
        fps = bpy.context.scene.render.fps
        start_time = self.start_time * fps
        key_interval = self.key_interval * fps
        max_len = self.max_len * fps

        msgs = compute_affixes(self.midi, max_prefix=start_time, max_suffix=max_len, suffix_after_end=False, split=1)
        last_value = 0
        for msg in msgs:
            intensity = self.get_intensity(msg)

            # Start
            self.animkey.animate(msg.start-msg.prefix, on=intensity*last_value, handle="VECTOR", type="BREAKDOWN")
            self.animkey.animate(msg.start, on=intensity, handle="VECTOR", type="EXTREME")

            # Fading
            frame = msg.start
            while True:
                frame += key_interval
                if frame > msg.start+msg.suffix:
                    break

                last_value = self.fade_func((frame-msg.start)/fps)

                if last_value < self.off_thres:
                    # Keyframe off
                    self.animkey.animate(frame, on=0, handle="VECTOR", type="JITTER")
                    last_value = 0
                    break

                self.animkey.animate(frame, on=intensity*last_value, handle="VECTOR", type="BREAKDOWN")

    @staticmethod
    def EXPONENTIAL(fac):
        """
        Exponential decay with factor ``fac`` (in units per second).
        """
        return lambda t: np.exp(-fac*t)

    @staticmethod
    def LINEAR(fac):
        """
        Linear decay with factor ``fac`` (in units per second).
        """
        return lambda t: 1 - fac*t


class IntensityWobble(Intensity):
    """
    Wobbles between 1 and -1 when hit.

    :Keyframe types:

        - JITTER: Resting (intensity = 0).
        - BREAKDOWN: Fading.
        - EXTREME: Max intensity (frame of hit).

    :Parameters:

        - fade_fac: Exponential decay factor in factor/wobble.

          - Default 0.7

        - period: Period of wobble in seconds.

          - Default: 1

        - off_thres: Threshold for intensity to be considered off.

          - Default: 0.01

        - note_end: Whether to set intensity to 0 at end of note. If false, will keep wobbling
          until next play.

          - Default: True  (stops when note ends).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fade_fac = kwargs.get("fade_fac", 0.7)
        self.period = kwargs.get("period", 1)
        self.off_thres = kwargs.get("off_thres", 0.01)
        self.note_end = kwargs.get("note_end", True)

    def animate(self):
        period = self.period * bpy.context.scene.render.fps

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
                self.animkey.animate(note.start, type="JITTER", handle="VECTOR", on=0)

            # Fading
            frame = note.start - period/2   # First wobble a little quicker.
            i = 0
            while True:
                intensity *= self.fade_fac
                next_frame = frame + period

                if next_frame > end_frame:
                    break
                if intensity < self.off_thres:
                    break

                curr_int = intensity if i % 2 == 0 else -intensity
                self.animkey.animate(next_frame, type="BREAKDOWN", on=curr_int)

                frame = next_frame
                i += 1

            last_ended = long_pause
