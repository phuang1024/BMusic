"""
Procedures operating on the note (i.e. pitch) of MIDI messages.

E.g. moving a striker to the correct position to play the notes.

On the other hand, animating the striker (e.g. with Hammer) doesn't depend
on what note (i.e. pitch) is being played; only the velocity of the note.
"""

__all__ = (
    "ToNote",
)

import bpy

from ..affix import compute_affixes
from ..anim import AnimKey
from .procedure import MusicProc


class ToNote(MusicProc):
    """
    Transition between notes (i.e. pitches).

    Parameters:

    animkey
        Keys:

            - ``0``, ``1``, etc.: Key for that note.

        Keys are strings, not ints.

    idle_time
        For each message, amount of time (sec) to wait before transitioning to the next message.
    """

    animkey: AnimKey
    idle_time: float = 0.1

    def animate(self):
        idle_time = self.idle_time * bpy.context.scene.render.fps

        msgs = compute_affixes(
            self.midi,
            max_prefix=idle_time / 2,
            max_suffix=idle_time / 2,
            suffix_after_end=True,
        )
        for msg in msgs:
            kwargs = {str(msg.note): 1}
            self.animkey.animate(msg.start-msg.prefix, **kwargs)
            self.animkey.animate(msg.end+msg.suffix, **kwargs)
