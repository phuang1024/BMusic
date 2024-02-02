__all__ = (
    "ProcMetaCls",
    "Procedure",
    "MusicProc",
    "ForEachProc",
)

import numpy as np

from ..midi import *


def _dummy():
    pass
function = type(_dummy)


class ProcMetaCls(type):
    """
    Metaclass for procedures.
    Automatically generates property documentation.

    Sets ``cls._params``, type set.

    In your class's docstring:

    1. Write a parameters section at the end; this is denoted with the text ``Parameters:``.
       See an existing class for an example.
    2. For each parameter, document it.
       Again, see an existing example.

    Example (put this at the end of docstring):

    .. code-block:: none

        Parameters:

        param1
            This is a parameter.
            Multiline descriptions are allowed.
            Must be 4 spaces indent.

        param2
            ...
    """

    def __new__(cls, name, bases, attrs):
        params, base_params = cls.get_params(bases, attrs)
        attrs["_params"] = params | base_params
        annotations = attrs.get("__annotations__", {})

        if attrs.get("_gen_docs", True):
            # Get and indent docstring.
            docstr = attrs.get("__doc__")
            if not isinstance(docstr, str):
                docstr = ""
            docstr = cls.reindent(docstr, 0).strip()

            # Extract parameter docs.
            param_docs = {}
            if "Parameters:" in docstr:
                ind = docstr.find("Parameters:")
                param_docstr = docstr[ind:].strip()
                docstr = docstr[:ind].strip()

                curr_param = None
                for i, line in enumerate(param_docstr.split("\n")):
                    # Skip first line.
                    if i == 0:
                        continue

                    if line.startswith(" ") and curr_param is not None:
                        param_docs[curr_param] += line[4:] + "\n"
                    else:
                        if line.strip():
                            curr_param = line.strip()
                            param_docs[curr_param] = ""

            # Add docs, type hints, and defaults.
            docstr += "\n\n:Parameters:\n\n"
            all_params = sorted(params) + sorted(base_params)
            if all_params:
                for param in all_params:
                    docstr += f"- ``{param}``"
                    if param in base_params:
                        docstr += " *(inherited)*"
                    else:
                        docstr += ":" + cls.reindent(param_docs.get(param, "").strip(), 2) + "\n\n"
                        if param in annotations:
                            docstr += f"  - **Type:** {annotations[param].__name__}\n"
                        if param in attrs:
                            docstr += f"  - **Default:** {attrs[param]}\n\n"
                    docstr += "\n"
            else:
                docstr += "None\n\n"

            attrs["__doc__"] = docstr

        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def get_params(bases, attrs) -> tuple[set[str], set[str]]:
        """
        Returns set of procedure parameters, extending from bases.
        """
        params = set()
        for key, value in attrs.items():
            if key.startswith("_"):
                continue
            if isinstance(value, (property, function)):
                continue
            params.add(key)
        if "__annotations__" in attrs:
            for key, value in attrs["__annotations__"].items():
                if key.startswith("_"):
                    continue
                if key in params:
                    continue
                params.add(key)

        base_params = set()
        for cls in bases:
            if hasattr(cls, "_params"):
                base_params.update(cls._params)

        return params, base_params

    @staticmethod
    def reindent(text: str, indent: int) -> str:
        max_indent = None
        for line in text.split("\n"):
            if not line.strip():
                continue
            curr_indent = len(line) - len(line.lstrip())
            if max_indent is None:
                max_indent = curr_indent
            else:
                max_indent = min(max_indent, curr_indent)
        if max_indent is None:
            return text

        lines = []
        for line in text.split("\n"):
            lines.append(" "*indent + line[max_indent:])
        return "\n".join(lines)



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
    - Then write the docstring in the class's docstring, explained further in the docs.
    - If you don't want automatic docs, set ``_gen_docs = False``.
    """

    _gen_docs = True
    _params: set[str] = set()
    """This is set by metaclass"""

    def __init__(self, **kwargs):
        """
        Don't override this method; this automatically sets parameters from kwargs.

        You can define the ``init`` method, which will be called from here.
        ``init`` is passed the same kwargs as this method.
        """
        for key, value in kwargs.items():
            if key in self._params:
                setattr(self, key, value)
        for param in self._params:
            if not hasattr(self, param):
                raise ValueError(f"Missing parameter: {param}")

        self.init(**kwargs)

    def init(self, **kwargs):
        """
        This is called after parameters are set from ``__init__``.

        Override this method to do custom initialization.
        """
        pass

    def animate(self):
        """
        Do all animation.
        """
        raise NotImplementedError("Subclass must implement animate()")


class MusicProc(Procedure):
    """
    Procedure superclass with utilities for music animation.

    Yes, this whole library is meant for music animation, but the base Procedure class
    is empty.
    This class has some stuff specific for music animation.

    Parameters:

    midi
        :class:`bmusic.MessageList` object containing messages to animate.
    """

    midi: MessageList


class ForEachProc(MusicProc):
    """
    Base class meant for animating the same thing on each message.
    e.g. for each message, do hammer; light up; etc.

    Intensity of message is interpolated from velocity, using given bounds.

    Parameters:

    min_intensity
        Minimum peak intensity. Happens when velocity is 0.

    max_intensity
        Maximum peak intensity. Happens when velocity is 127.
    """

    min_intensity: float = 0
    max_intensity: float = 1

    def get_intensity(self, msg: Message):
        """
        Returns interpolated intensity from velocity.
        """
        return np.interp(msg.velocity, [0, 127], [self.min_intensity, self.max_intensity])
