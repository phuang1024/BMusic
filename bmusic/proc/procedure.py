from typing import Any, Mapping


class Procedure:
    """
    Procedure base class.

    A procedure animates objects, with input parameters from the user.
    Example: Drum mallet animator, vibrating string, etc.

    Extend from this class to create your animator. Subclasses inherit
    available parameters from the parent class.

    Parameters
    ----------

    midi: Midi object.
    """

    params: Mapping[str, Any]

    def __init__(self, **kwargs):
        """
        Initialize the procedure.

        In the subclass, you may override this method, using more parameters.
        Subclasses inherit available parameters from the parent class.
        However, always call super().__init__() to initialize the parent class.
        """
        self.midi = kwargs.get("midi")

    def animate(self):
        """
        Do all animation.
        """
        raise NotImplementedError("Subclass must implement animate()")
