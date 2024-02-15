__all__ = (
    "Scheduling",
)

from typing import Callable

import bpy

from ..affix import compute_affixes
from ..anim import AnimKey
from ..midi import Message, MessageList
from .procedure import MusicProc


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
        Function to get cost between two note indexes.
        Costs are additive, and path of least cost is chosen.

    idle_time
        Time (sec) of pause when playing a message before available to move to next message.
    """

    animkeys: list[AnimKey]
    # WORKAROUND: lambda takes `_` argument which is `self`, which it doesn't need.
    cost_func: Callable[["Scheduling", int, int], float] = lambda _, i, j: abs(i-j)
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
