__all__ = (
    "Scheduling",
    "GreedyScheduling",
    "ChordScheduling",
)

from typing import Callable

import bpy
import numpy as np

from ..affix import compute_affixes
from ..anim import AnimKey
from ..midi import Message, MessageList, split_chords
from .procedure import MusicProc


def _default_cost_func(self, i, j):
    return abs(i - j)


class Scheduling(MusicProc):
    """
    Schedule limited number of agents (e.g. hammers) to switch between more notes to play.

    This procedure only moves the agents, but does not play the notes.
    You may want to combine it with something else e.g. Hammer.

    This is the base class; subclasses define the particular scheduling algorithm.
    Override the ``schedule`` method to implement an algorithm.

    Parameters:

    animkeys
        List of animation keys, each corresponding to an agent.
        Naturally, ``len(animkeys)`` is how many agents are available.

        Keys:

            - ``note0``, ``note1``, ``note2``, ...: Move to note index i.
              i.e. ``Message(note=24, ...)`` corresponds to key ``note24``.

    cost_func
        Function to get cost between two notes.
        Costs are additive, and path of least cost is chosen.

        Args:

            ``(self, i, j)``.

            ``i`` and ``j`` are notes (e.g. 21 = lowest A on piano).

    idle_time
        Time (sec) of pause when playing a message before available to move to next message.

    stay_to_end
        If true, hold an agent to a message until it ends.
        Else, agent can move as soon as it plays (i.e. when ``idle_time`` elapses).
    """

    @staticmethod
    def _default_cost_func(i, j):
        return abs(i - j)

    animkeys: list[AnimKey]
    cost_func: Callable[[int, int], float] = _default_cost_func
    idle_time: float = 0.1
    stay_to_end: bool = False

    def compute_cost(self, msg1: Message, msg2: Message) -> float:
        """
        Compute cost of playing ``msg1`` and ``msg2``.

        ``msg1.start < msg2.start``.

        Uses velocity;
        i.e. ``cost = velocity = distance / time``
        ``distance = self.cost_func(...)``
        """
        return self.cost_func(msg1.note, msg2.note) / (msg2.start - msg1.start)

    def schedule(self) -> list[MessageList]:
        """
        Compute which messages were scheduled to each agent.
        """
        raise NotImplementedError

    def animate(self) -> list[MessageList]:
        """
        Animates movement of each agent to their messages.
        Returns which messages were scheduled to each agent.

        :return: A list of :class:`bmusic.MessageList`s, each corresponding to 
            which messages the agent was scheduled to play.
        """
        idle_time = self.idle_time * bpy.context.scene.render.fps

        schedule = self.schedule()
        assert len(schedule) == len(self.animkeys)
        for i in range(len(self.animkeys)):
            animkey = self.animkeys[i]
            msgs = compute_affixes(schedule[i], max_prefix=idle_time/2, max_suffix=idle_time/2, suffix_after_end=self.stay_to_end)
            for msg in msgs:
                kwargs = {f"note{msg.note}": 1}
                animkey.animate(msg.start - msg.prefix, **kwargs)
                animkey.animate((msg.end if self.stay_to_end else msg.start) + msg.suffix, **kwargs)

        return schedule


class GreedyScheduling(Scheduling):
    """
    Greedy algorithm: Select agent with lowest cost for each message.
    """

    def schedule(self):
        schedule = [[] for _ in self.animkeys]

        for msg in self.midi:
            costs = [self.compute_cost(s[-1], msg) if s else 0 for s in schedule]
            index = np.argmin(costs)
            schedule[index].append(msg)

        return [MessageList(s) for s in schedule]


class ChordScheduling(Scheduling):
    """
    Greedy scheduling operating on chords instead of messages.

    Parameters:

    chord_threshold
        Passed to :func:`bmusic.midi.split_chords`. Units are seconds.
    """

    chord_threshold: float = 0.1

    def schedule(self):
        fps = bpy.context.scene.render.fps

        schedule = [[] for _ in self.animkeys]
        chords = split_chords(self.midi, threshold=self.chord_threshold*fps)

        for chord in chords:
            if len(chord) > len(self.animkeys):
                print(f"ChordScheduling: Chord has {len(chord)} notes; only {len(self.animkeys)} agents.")

            # Sort current state by note. (agent_index, curr_note)
            state = [(i, schedule[i][-1].note if schedule[i] else 0) for i in range(len(schedule))]
            state.sort(key=lambda x: x[1])
            state = [x[0] for x in state]

            min_cost = float("inf")
            best_i = 0
            for i in range(len(self.animkeys) - len(chord) + 1):
                cost = 0
                for j in range(len(chord)):
                    agent_i = state[i + j]
                    if schedule[agent_i]:
                        cost += self.compute_cost(schedule[agent_i][-1], chord[j])

                if cost < min_cost:
                    min_cost = cost
                    best_i = i

            for j in range(len(chord)):
                agent_i = state[best_i + j]
                schedule[agent_i].append(chord[j])

        return [MessageList(s) for s in schedule]
