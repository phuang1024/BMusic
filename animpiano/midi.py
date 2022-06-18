import mido

__all__ = (
    "Note",
    "parse_midi",
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


def parse_midi(midi: mido.MidiFile, fps):
    """
    Returns list of Note.
    """
    notes = []

    starts = [0] * 1000
    vels = [0] * 1000

    frame = 0
    for msg in midi:
        frame += msg.time * fps
        if msg.type.startswith("note_"):
            note = msg.note
            vel = msg.velocity if msg.type == "note_on" else 0
            if vel == 0:
                notes.append(Note(note, vels[note], starts[note], frame))
            else:
                starts[note] = frame
                vels[note] = vel

    return notes
