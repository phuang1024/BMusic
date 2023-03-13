__all__ = (
    "Affix",
    "compute_affixes",
)

from .midi import *


class Affix:
    """
    Prefix and suffix for one message.

    ``prefix`` and ``suffix`` are lengths in frames.
    Based on application, suffix is either time after **start**
    or **end**.
    """
    start: float
    end: float
    prefix: float
    suffix: float

    def __init__(self, start: float, end: float, prefix: float, suffix: float):
        self.start = start
        self.end = end
        self.prefix = prefix
        self.suffix = suffix

    def __repr__(self) -> str:
        return f"Affix({self.start}, {self.end}, {self.prefix}, {self.suffix})"


def compute_affixes(
        track: MessageList,
        split: float = 0.5,
        max_prefix: float = 1e9,
        max_suffix: float = 1e9,
        suffix_after_end: bool = False,
        hard_end: bool = False
        ) -> list[Affix]:
    """
    For each message, compute length of prefix and suffix.
    For example, a prefix may be a hammer anticipating,
    and a suffix may be the bounce back.

    Prefixes and suffixes don't overlap with the next message --- they
    will be shortened if next/prev note is too close.

    The result may look like this:

    .. code-block:: none

       Messages:    |--------|-----------|--|--|--------|
       Return:    <<|>>>---<<|>>>------<<|><|><|>>>---<<|>>>

    Each vertical line represents when each message plays. On the line
    marked ``Return``, ``<`` shows the duration of prefix and ``>`` for
    suffix.

    Notice how the max prefix length is 2, and the max suffix length
    is 3.

    Also notice how the prefix and suffix don't overlap with the next
    message --- they are shortened when necessary.

    If we take this result and interpret prefixes and suffixes as hammer
    actions as described above, this would create a smooth-looking
    animation.

    :param track: Track to process.
    :param split: Ratio between prefix and suffix when they overlap.
        ``0`` means completely prefix, and ``1`` means completely suffix.
    :param max_prefix: Maximum length of prefix in frames.
    :param max_suffix: Maximum length of suffix in frames.
    :param suffix_after_end: If true, suffix is after message ends. Else,
        suffix is immediately after message starts.
    :param hard_end: If true, cut off suffix when message ends (e.g. stop
        glowing when note is released). Otherwise, extend until ``max_suffix``
        (e.g. keep glowing indefinitely). Naturally, if used with suffix_after_end,
        suffix will be 0.
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

    ret = []

    for msg in track:
        # Compute prefix
        total_prev_time = msg.start - get_end(msg.prev(), -1e9)
        prefix_time = min(max_prefix, total_prev_time * (1-split))

        # Compute suffix
        total_next_time = msg.next_start() - get_end(msg, 0)
        suffix_time = min(max_suffix, total_next_time * split)

        # Adjust suffix if hard_end is True
        if hard_end:
            if suffix_after_end:
                suffix_time = 0
            else:
                suffix_time = min(suffix_time, msg.end - msg.start)

        # Add to list
        affix = Affix(msg.start, msg.end, prefix_time, suffix_time)
        ret.append(affix)

    return ret
