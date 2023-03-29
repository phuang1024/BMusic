__all__ = (
    "Hammer",
)

import bpy
import numpy as np

from ..anim import AnimKey
from .procedure import Procedure


class Hammer(Procedure):
    """
    Hammer movement: Resting, preparing, hitting, recoil, wobbling.

    :Keyframe types:

        - JITTER: Resting.
        - BREAKDOWN: Preparing to hit.
        - EXTREME: Hitting.
        - KEYFRAME: Recoil and oscillating.

    Parameters:

    animkey
        Animation key:

            - hit: Hitting.
            - prepare: Preparing to hit.
            - recoil: Bounce back after hit.

    prepare_time
        Duration (sec) of rest to prepare.

    hit_time
        Duration (sec) of prepare to hit movement.

    recoil_time
        Duration (sec) of hit to recoil movement.

    osc_period
        Duration (sec) of each oscillation after hit.

    osc_count
        Number of oscillations to perform.

    osc_decay
        Factor by which oscillation intensity decays each time.
    """

    animkey: AnimKey
    prepare_time: float = 0.15
    hit_time: float = 0.08
    recoil_time: float = 0.13
    osc_period: float = 0.35
    osc_count: int = 4
    osc_decay: float = 0.5

    def animate(self):
        fps = bpy.context.scene.render.fps
        hit_time = self.hit_time * fps
        prepare_time = self.prepare_time * fps
        recoil_time = self.recoil_time * fps
        osc_period = self.osc_period * fps
        osc_count = self.osc_count
        osc_decay = self.osc_decay

        before_dur = prepare_dur + hit_dur
        wobble_dur = wobble_period * wobble_count
        after_dur = wobble_dur + recoil_dur
        total_dur = before_dur + after_dur

        for i, note in enumerate(self.midi):
            last = note.prev_start
            next = note.next_start

            hit_intensity = np.interp(note.velocity, [0, 127], [0, 1])

            # Prepare to hit
            if note.start - last > total_dur:
                # Long time since, so reset to resting position.
                self.animkey.animate(note.start-before_dur, type="JITTER")

            prepare_frame = max(note.start-hit_dur, (note.start+last)/2)
            self.animkey.animate(prepare_frame, type="BREAKDOWN", prepare=hit_intensity)

            # Hit
            self.animkey.animate(note.start, type="EXTREME", handle="VECTOR", hit=1)

            # Wobble
            dur_limit = min(after_dur, next-note.start-before_dur)
            offset = recoil_dur

            for j in range(wobble_count):
                if offset >= dur_limit:
                    break
                intensity = wobble_decay ** (j+1)

                name = "prepare" if j % 2 == 0 else "hit"
                kwargs = {name: intensity}
                self.animkey.animate(note.start+offset, type="KEYFRAME", **kwargs)

                offset += wobble_period

            if next - before_dur > note.start + offset:
                # Long time until, so reset to resting position.
                self.animkey.animate(note.start+offset, type="JITTER")
