"""
Mechanical movements e.g. hammer, robot arm, etc.
"""

__all__ = (
    "Hammer",
    "Scheduling",
)

from copy import deepcopy
from math import tanh

import bpy
import numpy as np
from tqdm import tqdm

from ..midi import Midi
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
        Default: 0.15

    hit_dur: Duration (sec) of prepare to hit movement.
        Default: 0.08

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
        self.prepare_dur = kwargs.get("prepare_dur", 0.15)
        self.hit_dur = kwargs.get("hit_dur", 0.08)
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


class Scheduling(Procedure):
    """
    Schedule limited number of objects to switch between more notes to play.
    This procedure only moves the objects, but does not play the notes.
    You may want to combine it with something else e.g. Hammer.

    Parameters
    ----------

    animkeys: List of animation keys, each corresponding to a hammer.
        - move0, move1, move2, ...: Move to note index i.

    idle_time: Time (sec) of pause before moving on to next note.
        Default 0.1

    depth: Depth of search.
        Default: 3
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animkeys = kwargs.get("animkeys")
        self.idle_time = kwargs.get("idle_time", 0.1)
        self.depth = kwargs.get("depth", 3)

    def animate(self):
        """
        :return: A list. Each element is a Midi obj for the corresponding
            hammer to play.
        """
        self.fps = bpy.context.scene.render.fps  # For performance
        idle_time = self.idle_time * self.fps / 2
        notes_used = self.midi.notes_used

        # (note_ind, last_play_time)
        status = [[None, -1] for _ in self.animkeys]
        schedule = [[] for _ in self.animkeys]

        # Schedule notes
        print("BMusic: Scheduling: Scheduling notes...")
        min_reward = float("inf")
        for i, note in tqdm(enumerate(self.midi), total=len(self.midi.notes)):
            index, reward = self.best_choice(self.midi.notes, i, status, depth=self.depth)

            min_reward = min(min_reward, reward)
            schedule[index].append(note)
            status[index][0] = note.ind
            status[index][1] = note.start

        print(f"BMusic: Scheduling: min_reward={min_reward}")

        # Animate motion
        print("BMusic: Scheduling: Animate motion...")
        midis = list(map(Midi.from_notes, schedule))
        for i, mid in enumerate(midis):
            for note in mid:
                prev = note.prev_start
                next = note.next_start
                frames = [note.start]

                """
                thres = idle_time * 2.5   # Don't want too jarring.
                if note.start-prev > thres:
                    frames.append(note.start-idle_time)
                if next-note.start > thres:
                    frames.append(note.start+idle_time)
                """

                # Midi changed so can't use note.ind
                ind = notes_used.index(note.note)
                kwargs = {f"move{ind}": 1}
                for f in frames:
                    self.animkeys[i].animate(f, **kwargs)

        return midis

    def best_choice(self, notes, note_i, status, depth=1):
        """
        Compute which hammer to choose.

        :return: (hammer_i, reward)
        """
        assert depth >= 1

        count = len(status)
        note = notes[note_i]

        some_not_played = None in [s[0] for s in status]

        reward = []
        for i in range(count):
            if some_not_played:
                # First make sure each hammer plays
                rew = 1e6 if status[i][0] is None else 0
                reward.append(rew)
                continue

            dist = abs(note.ind - status[i][0])
            time = abs(note.start - status[i][1]) / self.fps

            dist = max(dist, 0.1)   # Divide by zero protection
            rew = tanh(30 * time / dist)

            if depth > 1 and note_i < len(notes)-1:
                new_status = deepcopy(status)
                new_status[i][0] = note.ind
                new_status[i][1] = note.start
                _, depth_rew = self.best_choice(notes, note_i+1, new_status, depth-1)

                rew += depth_rew

            reward.append(rew)

        index = np.argmax(reward)
        reward = max(reward)

        return index, reward
