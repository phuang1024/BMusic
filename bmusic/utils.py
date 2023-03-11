__all__ = (
    "message_affixes",
)

from .midi import *


def message_affixes(
        track: MessageList,
        split: float = 0.5,
        max_prefix: float = 1e9,
        max_suffix: float = 1e9,
        use_end: bool = False):
    """
    For each message, compute length of prefix and suffix.
    For example, a prefix may be a hammer anticipating,
    and a suffix may be the bounce back.

    Prefixes and suffixes don't overlap with the next message.
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
    :param use_end: If true, cut off suffix when message ends (e.g. stop
        glowing when note is released). Otherwise, extend until ``max_suffix``
        (e.g. keep glowing indefinitely).
    :return: List of tuples, one for each message. Each tuple is
        ``(prefix, message, suffix)`` where ``message`` is the original
        message's start time. ``prefix`` and ``suffix`` are **absolute** framestamps
        for the start and end of the prefix and suffix, respectively.
    """
