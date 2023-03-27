"""
Procedures relating to intensity of something.
e.g. light, piano key's depression, string's vibration, etc.
"""

__all__ = (
    "Intensity",
    "IntensityOnOff",
    "IntensityFade",
    "IntensityOsc",
)

from math import cos, pi
from typing import Callable

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

        - min_intensity: Minimum peak intensity. Happens when velocity is 0.

          - Default: 0

        - max_intensity: Maximum peak intensity. Happens when velocity is 127.

          - Default: 1

        - use_velocity: Whether to scale peak intensity based on message velocity.
          If True, intensity is scaled from ``min_intensity`` to ``max_intensity``.
          Otherwise, intensity is always ``max_intensity``.

          - Default: True
    """

    animkey: AnimKey
    min_intensity: float
    max_intensity: float
    use_velocity: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animkey = kwargs.get("animkey")
        self.min_intensity = kwargs.get("min_intensity", 0)
        self.max_intensity = kwargs.get("max_intensity", 1)
        self.use_velocity = kwargs.get("use_velocity", True)

    def get_intensity(self, msg: Message):
        """
        Returns either msg.velocity/127 or 1 depending on self.use_velocity
        """
        if self.use_velocity:
            return np.interp(msg.velocity, [0, 127], [self.min_intensity, self.max_intensity])
        else:
            return self.max_intensity


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
          predefined functions ``bmusic.utils``

          - Default ``EXPONENTIAL(0.6)`` (exponential decay at 0.6/sec)

        - start_time: Time, in seconds, from off to initial on.

          - Default: 0.05

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

    fade_func: Callable[[float], float]
    start_time: float
    key_interval: float
    off_thres: float
    max_len: float
    note_end: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fade_func = kwargs.get("fade_func", EXPONENTIAL(0.6))
        self.start_time = kwargs.get("start_time", 0.05)
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


class IntensityOsc(Intensity):
    """
    Sinusoidal oscillation when a note is playing.
    Specifically, ``anim(t)`` (the value animated) ``= intensity(t) * cos(t*...)``
    The user provides an ``intensity`` function; e.g. exponential decay. This is then
    multiplied by a sinusoidal function.

    :Keyframe types:

        - JITTER: Resting (intensity = 0).
        - BREAKDOWN: Oscillating and fading.
        - EXTREME: Max intensity (frame of hit).

    :Parameters:

        Many parameters are same as :class:`IntensityFade`. See that class for docs about
        those parameters.

        - fade_func:

          - Default: ``EXPONENTIAL(0.6)``

        - period: Period of oscillation in seconds.

          - Default: 1

        - start_time:

          - Default: 0.05

        - key_interval: Note: A lower interval may be required than IntensityFade for the
          same smooth appearance.

          - Default: 0.1

        - off_thres:

          - Default: 0.001

        - max_len:

          - Default: 60

        - note_end:

          - Default: True
    """

    fade_func: Callable[[float], float]
    period: float
    start_time: float
    key_interval: float
    off_thres: float
    max_len: float
    note_end: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fade_func = kwargs.get("fade_func", EXPONENTIAL(0.6))
        self.period = kwargs.get("period", 1)
        self.start_time = kwargs.get("start_time", 0.05)
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

                time = (frame-msg.start) / fps
                last_value = self.fade_func(time)

                if last_value < self.off_thres:
                    # Keyframe off
                    self.animkey.animate(frame, on=0, handle="VECTOR", type="JITTER")
                    last_value = 0
                    break

                value = intensity * last_value * cos(2*pi*time/self.period)
                self.animkey.animate(frame, on=value, handle="VECTOR", type="BREAKDOWN")
