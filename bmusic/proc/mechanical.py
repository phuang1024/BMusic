"""
Mechanical movements e.g. hammer, robot arm, etc.
"""

__all__ = (
    "Hammer",
)

import bpy
import numpy as np

from .procedure import Procedure


class Hammer(Procedure):
    """
    Hammer movement: Resting, preparing, hitting, recoil, wobbling.

    Keyframe types:
    - JITTER: Resting.
    - BREAKDOWN: Preparing to hit.
    - EXTREME: Hitting.
    - KEYFRAME: Recoil and wobbling.

    Parameters
    ----------

    animkey: Animation key:
        - hit: Hitting.
        - prepare: Preparing to hit.
        - recoil: Bounce back after hit.

    prepare_dur: Duration (sec) of rest to prepare.
        Default: 0.18

    hit_dur: Duration (sec) of prepare to hit movement.
        Default: 0.1

    recoil_dur: Duration (sec) of hit to recoil movement.
        Default: 0.13

    wobble_period: Duration (sec) of each wobble.
        Default: 0.35

    wobble_count: Number of wobbles to perform.
        Default: 4

    wobble_decay: Factor by which wobble intensity decays each time.
        Default: 0.5
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animkey = kwargs.get("animkey")
        self.prepare_dur = kwargs.get("prepare_dur", 0.18)
        self.hit_dur = kwargs.get("hit_dur", 0.1)
        self.recoil_dur = kwargs.get("recoil_dur", 0.13)
        self.wobble_period = kwargs.get("wobble_period", 0.35)
        self.wobble_count = kwargs.get("wobble_count", 4)
        self.wobble_decay = kwargs.get("wobble_decay", 0.5)

    def animate(self):
        fps = bpy.context.scene.render.fps
        hit_dur = self.hit_dur * fps
        prepare_dur = self.prepare_dur * fps
        recoil_dur = self.recoil_dur * fps
        wobble_period = self.wobble_period * fps
        wobble_count = self.wobble_count
        wobble_decay = self.wobble_decay

        before_dur = prepare_dur + hit_dur
        wobble_dur = wobble_period * wobble_count
        after_dur = wobble_dur + recoil_dur
        total_dur = before_dur + after_dur

        for i, note in enumerate(self.midi):
            last = note.prev.start if note.prev else -1e9
            next = note.next_start

            hit_intensity = np.interp(note.velocity, [0, 127], [0, 1])

            # Prepare to hit
            if note.start - last > total_dur:
                # Long time since, so reset to resting position.
                self.animkey.animate(note.start-before_dur, type="JITTER")

            prepare_frame = max(note.start-hit_dur, (note.start+last)/2)
            self.animkey.animate(prepare_frame, type="BREAKDOWN", prepare=hit_intensity)

            # Hit
            self.animkey.animate(note.start, type="EXTREME", handle="VECTOR", hit=hit_intensity)

            # Wobble
            dur_limit = min(after_dur, next-note.start-before_dur)
            offset = recoil_dur

            for j in range(wobble_count):
                if offset >= dur_limit:
                    break
                intensity = hit_intensity * wobble_decay ** (j+1)

                name = "prepare" if j % 2 == 0 else "hit"
                kwargs = {name: intensity}
                self.animkey.animate(note.start+offset, type="KEYFRAME", **kwargs)

                offset += wobble_period

            if next - before_dur > note.start + offset:
                # Long time until, so reset to resting position.
                self.animkey.animate(note.start+offset, type="JITTER")
