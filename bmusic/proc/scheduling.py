__all__ = (
    "Scheduling",
    "GreedyScheduling",
)

from typing import Callable

import bpy
import numpy as np

from ..affix import compute_affixes
from ..anim import AnimKey
from ..midi import Message, MessageList
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
    """

    @staticmethod
    def _default_cost_func(i, j):
        return abs(i - j)

    animkeys: list[AnimKey]
    cost_func: Callable[[int, int], float] = _default_cost_func
    idle_time: float = 0.1

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
            msgs = compute_affixes(schedule[i], max_prefix=idle_time/2, max_suffix=idle_time/2)
            for msg in msgs:
                kwargs = {f"note{msg.note}": 1}
                animkey.animate(msg.start-msg.prefix, **kwargs)
                animkey.animate(msg.end+msg.suffix, **kwargs)

        return schedule


class GreedyScheduling(Scheduling):
    """
    Greedy algorithm: Select agent with lowest cost for each message.
    """

    def schedule(self):
        print(self.animkeys)
        schedule = [[] for _ in self.animkeys]

        for msg in self.midi:
            costs = [self.compute_cost(s[-1], msg) if s else 0 for s in schedule]
            index = np.argmin(costs)
            schedule[index].append(msg)

        return [MessageList(s) for s in schedule]
