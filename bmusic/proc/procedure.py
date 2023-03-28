__all__ = (
    "Procedure",
)

from ..midi import *


def _dummy():
    pass
function = type(_dummy)


class ProcMetaCls(type):
    """
    Metaclass for procedures.
    Automatically generates property documentation.
    """

    def __new__(cls, name, bases, attrs):
        if attrs.get("_gen_docs", True):
            docstr = attrs.get("__doc__")
            if not isinstance(docstr, str):
                docstr = ""
            docstr = docstr.strip() + "\n\n"
            docstr += ":Parameters:\n\n"

            params = []
            for key, value in attrs.items():
                if key.startswith("_"):
                    continue
                if isinstance(value, (property, function)):
                    continue
                params.append(key)
            for key, value in attrs["__annotations__"].items():
                if key.startswith("_"):
                    continue
                if key in params:
                    continue
                params.append(key)

            print(params)

        return super().__new__(cls, name, bases, attrs)


class Procedure(metaclass=ProcMetaCls):
    """
    Procedure base class.

    A procedure animates objects, with input parameters from the user.
    Procedures are generalized: For example, a hammer procedure can be applied
    to a drum mallet, a piano key, etc.

    Extend from this class to create your animator. Subclasses inherit
    available parameters from the parent class.

    This class uses the :class:`bmusic.ProcMetaCls` metaclass to automatically
    generate property docs.

    - For each property, type hint and/or define a default value in the class.
    - Define another variable with the same name, but with a leading underscore,
      which holds the docstring.
    - If you don't want automatic docs, set ``_gen_docs = False``.

    :Parameters:
        - midi: :class:`bmusic.MessageList` object containing messages to animate.
    """

    _gen_docs = True

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
