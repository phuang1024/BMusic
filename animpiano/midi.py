import mido

__all__ = (
    "Note",
    "parse_midi",
    "notes_used",
)


class Note:
    """
    Note with absolute start and end time in frames.
    """
    note: int
    velocity: int
    start: float
    end: float

    def __init__(self, note, velocity, start, end):
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end = end

    def __repr__(self):
        return (f"animpiano.Note(note={self.note}, velocity={self.velocity}, "
                f"start={self.start}, end={self.end})")


def parse_midi(midi: mido.MidiFile, fps, offset=0):
    """
    Returns many instances of Note. First note's start is frame 0 + offset.

    :param offset: Added to start and end framestamps.
    """
    notes = []

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
                yield n
            else:
                starts[note] = frame
                vels[note] = vel


def notes_used(midi: mido.MidiFile):
    """
    Returns set of all notes used.
    """
    notes = []
    for msg in midi:
        if hasattr(msg, "note"):
            notes.append(msg.note)

    return set(notes)
