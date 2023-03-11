from typing import Optional, Sequence

import bpy
import mido

__all__ = (
    "Note",
    "NoteList",
    "parse_midi"
)


class Note:
    """
    Note with absolute start and end time in frames.
    Also supports linked-list like behavior within track.
    """
    note: int
    velocity: int
    start: float
    end: float

    def __init__(self, note, velocity, start, end, notelist: Optional["NoteList"] = None, index: Optional[int] = None):
        """
        :param notelist: NoteList object this note belongs to.
        :param index: Index of this note in the track. Allows for linked-list behavior.
        """
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end = end

        self.notelist = notelist
        self.index = index

    def __repr__(self):
        return (f"bmusic.Note(note={self.note}, velocity={self.velocity}, "
                f"start={self.start}, end={self.end})")

    def copy(self) -> "Note":
        """
        Copy this note.
        """
        return Note(self.note, self.velocity, self.start, self.end, self.notelist, self.index)

    def diff(self, other: "Note") -> float:
        """
        Calculate difference in frames between this note and another's start.
        Positive if this note starts after other.
        """
        return self.start - other.start

    def next(self) -> Optional["Note"]:
        """
        Get next note in notelist.
        """
        assert self.index is not None
        assert self.notelist is not None

        ind = self.index + 1
        if ind >= len(self.notelist._notes):
            return None
        return self.notelist._notes[ind]

    def next_start(self, fallback: float = 1e9) -> float:
        """
        Timestamp of next note's start.

        :param fallback: Value to return if no next note.
        """
        return self.next.start if self.next else fallback

    def prev(self) -> Optional["Note"]:
        """
        Get previous note in notelist.
        """
        assert self.index is not None
        assert self.notelist is not None

        ind = self.index - 1
        if ind < 0:
            return None
        return self.notelist._notes[ind]

    def prev_start(self, fallback: float = -1e9) -> float:
        """
        Timestamp of previous note's start.

        :param fallback: Value to return if no previous note.
        """
        return self.prev.start if self.prev else fallback

    def prev_end(self, fallback: float = -1e9) -> float:
        """
        Timestamp of previous note's end.

        :param fallback: Value to return if no previous note.
        """
        return self.prev.end if self.prev else fallback


class NoteList:
    """
    Sequence of notes sorted by start time.
    """

    def __init__(self, notes: Optional[Sequence[Note]] = None):
        """
        Initialize from notes.
        Also associates each note with self.
        """
        if notes is None:
            notes = []

        self._notes = []
        for note in notes:
            note = note.copy()
            note.notelist = self
            note.index = len(self._notes)
            self._notes.append(note)

        self._notes.sort(key=lambda n: n.start)
        self._noteset = sorted(set(n.note for n in self._notes))

    def __iter__(self):
        yield from self._notes

    def __len__(self):
        return len(self._notes)

    def __getitem__(self, item):
        return self._notes[item]

    def __repr__(self):
        return f"bmusic.NoteList({self._notes})"

    def noteset(self):
        """
        Set of all notes used in this track.
        """
        return self._noteset

    def length(self) -> float:
        """
        Duration, in frames, between first note's start and last note's end.
        Does not regard offset.
        """
        return self._notes[-1].end - self._notes[0].start
    
    def filter_notes(self, notes: Sequence[int]) -> "NoteList":
        """
        Only keep notes in the given list.
        """
        return NoteList([n for n in self._notes if n.note in notes])

    def split_notes(self):
        """
        Split into multiple tracks, each containing only one note.
        """
        for note in self.noteset():
            yield NoteList([n for n in self._notes if n.note == note])


def parse_midi(path: str, offset: float = 0, fps: float | None = None) -> NoteList:
    """
    Parse MIDI from a file.

    :param path: Path to midi file.
    :param offset: Offset in frames to add to all notes.
    :param fps: Frames per second (None for blender fps)
    """
    notes = []

    fps = bpy.context.scene.render.fps if fps is None else fps
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
                n = Note(note, vels[note], starts[note]+offset, frame+offset)
                notes.append(n)
            else:
                starts[note] = frame
                vels[note] = vel

    return NoteList(notes)
