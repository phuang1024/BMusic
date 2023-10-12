__all__ = (
    "Hammer",
)

import bpy

from ..affix import compute_affixes
from ..anim import AnimKey
from ..utils import *
from .procedure import ForEachProc


class Hammer(ForEachProc):
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
        osc_count = self.osc_count + 1   # for ending "rest" oscillation.
        osc_decay = self.osc_decay

        before_time = prepare_time + hit_time
        osc_time = osc_period * osc_count
        after_time = osc_time + recoil_time

        msgs = compute_affixes(self.midi, max_prefix=before_time, max_suffix=after_time, split=0)
        prev_ended = True
        for msg in msgs:
            if prev_ended:
                # Need to key at rest first.
                self.animkey.animate(msg.start - before_time, type="JITTER")

            # Prepare
            intensity = self.get_intensity(msg)
            self.animkey.animate(msg.start - msg.prefix/2, type="BREAKDOWN", prepare=intensity)

            # Hit
            self.animkey.animate(msg.start, type="EXTREME", handle="VECTOR", hit=1)

            # Oscillation
            prev_ended = False
            frame = recoil_time
            for i in range(osc_count):
                if frame >= msg.suffix:
                    break

                if i == osc_count-1:
                    value = 0
                else:
                    value = intensity * osc_decay ** (i+1)
                name = "prepare" if i % 2 == 0 else "hit"
                kwargs = {name: value}
                self.animkey.animate(msg.start + frame, type="KEYFRAME", **kwargs)

                frame += osc_period

            # Ending
            if msg.suffix >= after_time:
                self.animkey.animate(msg.start + frame, type="JITTER")
                prev_ended = True
