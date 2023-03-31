__all__ = (
    "Scheduling",
)

from copy import deepcopy
from math import tanh
from typing import Callable

import bpy
import numpy as np
from tqdm import tqdm

from ..anim import AnimKey
from ..midi import MessageList
from .procedure import Procedure


class Scheduling(Procedure):
    """
    Schedule limited number of objects to switch between more notes to play.
    This procedure only moves the objects, but does not play the notes.
    You may want to combine it with something else e.g. Hammer.

    Parameters:

    animkeys
        List of animation keys, each corresponding to a hammer.

            - ``move0``, ``move1``, ``move2``, ...: Move to note index i.

    dist_f
        Function to get distance or cost between two note indexes.

    idle_time
        Time (sec) of pause before moving on to next note.

    depth
        Depth of search.
    """

    animkeys: list[AnimKey]
    dist_f: Callable[[int, int], float] = lambda i, j: abs(i-j)
    idle_time: float = 0.1
    depth: int = 3

    def animate(self):
        """
        Animates movement of each object to their messages.
        Returns which messages were scheduled to each object.

        :return: A list. Each element is a :class:`bmusic.MessageList` obj for the corresponding
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
            status[index][1] = max(note.start, status[index][1])

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

            dist = self.dist_f(note.ind, status[i][0])
            dist = max(dist, 0.01)   # Divide by zero protection
            time = abs(note.start - status[i][1]) / self.fps
            rew = tanh(30 * time / dist)

            if depth > 1 and note_i < len(notes)-1:
                new_status = deepcopy(status)
                new_status[i][0] = note.ind
                new_status[i][1] = note.start
                _, depth_rew = self.best_choice(notes, note_i+1, new_status, depth-1)

                rew += depth_rew

            reward.append(rew)

        index = np.argmax(reward)
        rew = reward[index]

        return index, rew
