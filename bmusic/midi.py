from typing import List, Sequence

import bpy
import mido

__all__ = (
    "Note",
    "Midi",
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

    def __init__(self, note, velocity, start, end, midi: "Midi", index: int):
        """
        :param midi: Midi object this note belongs to.
        :param index: Index of this note in the track. Allows for linked-list.
        """
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end = end

        self.midi = midi
        self.index = index

    def __repr__(self):
        return (f"animpiano.Note(note={self.note}, velocity={self.velocity}, "
                f"start={self.start}, end={self.end})")

    def diff(self, other: "Note") -> float:
        """
        Calculate difference in frames between this note and another's start.
        Positive if this note starts after other.
        """
        return self.start - other.start

    @property
    def ind(self) -> int:
        """
        Index of self.note in self.midi.
        """
        return self.midi.notes_used.index(self.note)

    @property
    def next(self) -> "Note":
        """
        Get next note in midi.
        """
        ind = self.index + 1
        if ind >= len(self.midi.notes):
            return None
        return self.midi.notes[ind]

    @property
    def next_start(self) -> float:
        """
        Timestamp of next note's start.
        1e9 if no next note.
        """
        return self.next.start if self.next else 1e9

    @property
    def prev(self) -> "Note":
        """
        Get previous note in midi.
        """
        ind = self.index - 1
        if ind < 0:
            return None
        return self.midi.notes[ind]

    @property
    def prev_start(self) -> float:
        """
        Timestamp of previous note's start.
        -1e9 if no previous note.
        """
        return self.prev.start if self.prev else -1e9

    @property
    def prev_end(self) -> float:
        """
        Timestamp of previous note's end.
        -1e9 if no previous note.
        """
        return self.prev.end if self.prev else -1e9


class Midi:
    """
    Parse a midi file, combining all tracks.
    """

    def __init__(self, path: str = None, offset: float = 0) -> None:
        """
        Parse a midi file.

        :param path: Path to midi file.
        :param fps: Frames per second.
        :param offset: Offset in frames to add to all notes.
        """
        self.notes = []

        if path is None:
            return

        fps = bpy.context.scene.render.fps
        midi = mido.MidiFile(path)

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
                    n = Note(note, vels[note], starts[note]+offset, frame+offset, self, len(self.notes))
                    self.notes.append(n)
                else:
                    starts[note] = frame
                    vels[note] = vel

        self._init()

    def __iter__(self):
        return iter(self.notes)

    def __len__(self):
        return len(self.notes)

    @classmethod
    def from_notes(cls, notes: Sequence[Note]) -> "Midi":
        """
        Create a midi from a list of notes.
        """
        midi = Midi(None, None)
        midi.notes = [Note(n.note, n.velocity, n.start, n.end, midi, i) for i, n in enumerate(notes)]
        midi._init()
        return midi

    @property
    def length(self) -> float:
        """
        Duration, in frames, between first note's start and last note's end.
        Does not regard offset.
        """
        return self.notes[-1].end - self.notes[0].start
    
    def filter_notes(self, good: Sequence[int]) -> "Midi":
        """
        Filter notes to only those in good.
        """
        return Midi.from_notes(n for n in self.notes if n.note in good)

    def _init(self):
        """
        More initializing.
        """
        self.notes_used = sorted(set(n.note for n in self.notes))
