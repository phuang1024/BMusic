"""
Utilities for computing and representing affixes.

See docs for more info.
"""

__all__ = (
    "AffixMessage",
    "compute_affixes",
)

import numpy as np

from .midi import *


class AffixMessage(Message):
    """
    Prefix and suffix extension.

    ``prefix`` and ``suffix`` are lengths in frames.
    Based on application, suffix is either time after **start**
    or **end**.
    """

    prefix: float
    suffix: float

    def __repr__(self) -> str:
        return f"AffixMessage(msg={super().__repr__()}, prefix={self.prefix}, suffix={self.suffix})"


def compute_affixes(
        track: MessageList,
        split: float = 0.5,
        max_prefix: float = 1e9,
        max_suffix: float = 1e9,
        suffix_after_end: bool = False,
        hard_end: bool = False
        ) -> list[AffixMessage]:
    """
    For each message (taking into account neighboring messages in the track),
    compute length of prefix and suffix.

    For example, a prefix may be a hammer anticipating, and a suffix may be the
    bounce back.

    Prefixes and suffixes don't overlap with the next message --- they will be
    shortened if next/prev note is too close.

    The result may look like this:

    .. code-block:: none

       Messages:    |--------|-----------|--|--|--------|
       Return:    <<|>>>---<<|>>>------<<|><|><|>>>---<<|>>>

    Each vertical line represents when each message plays. On the line marked
    ``Return``, ``<`` shows the duration of prefix and ``>`` for suffix.

    Notice how the max prefix length is 2, and the max suffix length is 3.

    Also notice how the prefix and suffix don't overlap with the next message
    --- they are shortened when necessary.

    If we take this result and interpret prefixes and suffixes as hammer actions
    as described above, this would create a smooth-looking animation.

    See the docs page for more details.

    :param track: Track to process.
    :param split: Ratio between prefix and suffix when they overlap.
        ``0`` means completely prefix, and ``1`` means completely suffix.
    :param max_prefix: Maximum length of prefix in frames.
    :param max_suffix: Maximum length of suffix in frames.
    :param suffix_after_end: If true, suffix is after message ends. Else,
        suffix is immediately after message starts.
    :param hard_end: If true, cut off suffix when message ends (e.g. stop
        glowing when note is released). Otherwise, extend until ``max_suffix``
        (e.g. keep glowing indefinitely). Naturally, if used with
        ``suffix_after_end``, suffix will be 0.
    :return: List of Affix
    """
    def get_end(msg, fallback):
        """
        Get suffix starting point of message;
        returns msg.end if suffix_after_end is True,
        else msg.start
        """
        if msg is None:
            return fallback
        return msg.end if suffix_after_end else msg.start

    def get_msg_pair_info(msg1, msg2):
        """
        Returns convenient info about timestamps of prefix, overlap, etc.

        ``msg1`` and ``msg2`` should be two consecutive messages, where
        msg1 <= msg2.

        Return:
            nominal_suffix: msg1's suffix timestamp, disregarding overlap.
            nominal_prefix: msg2's prefix timestamp, disregarding overlap.
        """
        suffix = get_end(msg1, -1e9) + max_suffix
        prefix = msg2.start - max_prefix if msg2 is not None else 1e9
        return {
            "nominal_suffix": suffix,
            "nominal_prefix": prefix,
            "msg1": get_end(msg1, -1e9),
            "msg2": msg2.start if msg2 is not None else 1e9,
        }

    ret = []

    for msg in track:
        # Compute prefix
        info = get_msg_pair_info(msg.prev(), msg)
        if info["nominal_suffix"] > info["nominal_prefix"]:
            split_point = np.interp(split, [0, 1], [info["nominal_prefix"], info["nominal_suffix"]])
            split_point = np.clip(split_point, info["msg1"], info["msg2"])
            prefix_time = msg.start - split_point
        else:
            prefix_time = max_prefix

        # Compute suffix
        info = get_msg_pair_info(msg, msg.next())
        if info["nominal_suffix"] > info["nominal_prefix"]:
            split_point = np.interp(split, [0, 1], [info["nominal_prefix"], info["nominal_suffix"]])
            split_point = np.clip(split_point, info["msg1"], info["msg2"])
            suffix_time = split_point - get_end(msg, msg.start)
        else:
            suffix_time = max_suffix

        # Adjust suffix if hard_end is True
        if hard_end:
            if suffix_after_end:
                suffix_time = 0
            else:
                suffix_time = min(suffix_time, msg.end - msg.start)

        # Add to list
        affix = AffixMessage(msg.note, msg.velocity, msg.start, msg.end)
        affix.prefix = prefix_time
        affix.suffix = suffix_time
        ret.append(affix)

    return ret
