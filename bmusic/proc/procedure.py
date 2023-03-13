__all__ = (
    "Procedure",
)

from ..midi import *


class Procedure:
    """
    Procedure base class.

    A procedure animates objects, with input parameters from the user.
    Procedures are generalized: For example, a hammer procedure can be applied
    to a drum mallet, a piano key, etc.

    Extend from this class to create your animator. Subclasses inherit
    available parameters from the parent class.

    :Parameters:
        - midi: :class:`bmusic.MessageList` object containing messages to animate.
    """

    midi: MessageList

    def __init__(self, **kwargs):
        """
        Initialize the procedure.

        In the subclass, you may override this method, using more parameters.
        Subclasses inherit available parameters from the parent class.

        Always call ``super().__init__()`` to initialize the parent class.
        """
        self.midi = kwargs.get("midi")

    def animate(self):
        """
        Do all animation.
        """
        raise NotImplementedError("Subclass must implement animate()")
