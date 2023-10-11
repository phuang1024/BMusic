"""
"note" refers to a pitch, represented as an integer in MIDI.
For example, there are 88 notes on a piano.

"message" refers to an instance of a note being played.
For example, this MIDI file has 100 messages,
using a total of 10 different notes.
"""

from typing import Generator, Optional, Sequence

import bpy
import mido

__all__ = (
    "Message",
    "MessageList",
    "parse_midi",
    "split_chords",
)


class Message:
    """
    Message with absolute start and end time in frames.
    Also supports linked-list like behavior within track.
    """

    note: int
    velocity: int
    start: float
    end: float

    def __init__(self, note, velocity, start, end, msglist: Optional["MessageList"] = None, index: Optional[int] = None):
        """
        :param msglist: MessageList object this message belongs to.
        :param index: Index of this message in the track. Allows for linked-list behavior.
        """
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end = end

        self.msglist = msglist
        self.index = index

    def __repr__(self):
        return (f"bmusic.Message(note={self.note}, velocity={self.velocity}, "
                f"start={self.start}, end={self.end})")

    def copy(self) -> "Message":
        return Message(self.note, self.velocity, self.start, self.end, self.msglist, self.index)

    def diff(self, other: "Message") -> float:
        """
        Calculate difference in frames between this message and another's start.
        Positive if this message starts after other.
        """
        return self.start - other.start

    def next(self) -> Optional["Message"]:
        """
        Get next message in msglist.
        """
        assert self.index is not None
        assert self.msglist is not None

        ind = self.index + 1
        if ind >= len(self.msglist._messages):
            return None
        return self.msglist._messages[ind]

    def next_start(self, fallback: float = 1e9) -> float:
        """
        Timestamp of next message's start.

        :param fallback: Value to return if no next message.
        """
        return self.next().start if self.next() else fallback

    def prev(self) -> Optional["Message"]:
        """
        Get previous message in msglist.
        """
        assert self.index is not None
        assert self.msglist is not None

        ind = self.index - 1
        if ind < 0:
            return None
        return self.msglist._messages[ind]

    def prev_start(self, fallback: float = -1e9) -> float:
        """
        Timestamp of previous message's start.

        :param fallback: Value to return if no previous message.
        """
        return self.prev().start if self.prev() else fallback

    def prev_end(self, fallback: float = -1e9) -> float:
        """
        Timestamp of previous message's end.

        :param fallback: Value to return if no previous message.
        """
        return self.prev().end if self.prev() else fallback


class MessageList:
    """
    Sequence of messages sorted by start time.
    """

    def __init__(self, messages: Optional[Sequence[Message]] = None):
        """
        Initialize from message.
        Creates copies of each message.
        Also associates each message with self.
        """
        if messages is None:
            messages = []

        self._messages = []
        for msg in messages:
            msg = msg.copy()
            msg.msglist = self
            msg.index = len(self._messages)
            self._messages.append(msg)

        self._messages.sort(key=lambda n: n.start)
        self._noteset = sorted(set(n.note for n in self._messages))

    def __iter__(self) -> Generator[Message, None, None]:
        yield from self._messages

    def __len__(self):
        return len(self._messages)

    def __getitem__(self, item):
        return self._messages[item]

    def __repr__(self):
        return f"bmusic.MessageList({self._messages})"

    def noteset(self):
        """
        Set of all notes used in this track.
        """
        return self._noteset

    def duration(self) -> float:
        """
        Duration, in frames, between first msg's start and last msg's end.
        """
        return self._messages[-1].end - self._messages[0].start
    
    def filter_notes(self, notes: Sequence[int]) -> "MessageList":
        """
        Only keep messages with note in the given list.
        """
        return MessageList([n for n in self._messages if n.note in notes])

    def split_notes(self):
        """
        Split into multiple tracks, each containing only one note.
        """
        for note in self.noteset():
            yield MessageList([n for n in self._messages if n.note == note])


def parse_midi(path: str, offset: float = 0, fps: Optional[float] = None) -> MessageList:
    """
    Parse MIDI from a file.

    :param path: Path to midi file.
    :param offset: Duration in frames of first message's start.
    :param fps: Frames per second (None for blender fps)
    """
    notes = []

    if fps is None:
        fps = bpy.context.scene.render.fps
    midi = mido.MidiFile(path)

    # State of the last key press of note i.
    starts = [0] * 1000
    vels = [0] * 1000

    frame = 0
    started = False
    for msg in midi:
        if started:
            frame += msg.time * fps

        if msg.type.startswith("note_"):
            started = True
            note = msg.note
            vel = msg.velocity if msg.type == "note_on" else 0
            if vel == 0:
                n = Message(note, vels[note], starts[note]+offset, frame+offset)
                notes.append(n)
            else:
                starts[note] = frame
                vels[note] = vel

    return MessageList(notes)


def split_chords(midi: MessageList, threshold: float) -> list[list[Message]]:
    """
    Split a MIDI track into chords --- messages that play roughly at the same time.
    Messages less than threshold apart will be combined into one chord.
    Threshold units are whatever midi units are. Most likely frames.
    """
    chords = []

    last_time = None
    chord = []
    for msg in midi:
        if last_time is None:
            chord.append(msg)
        elif abs(msg.start - last_time) < threshold:
            chord.append(msg)
        else:
            chords.append(chord)
            chord = [msg]

    return chords
