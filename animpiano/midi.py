class Note:
    """
    Note with start and stop time.
    """
    note: int
    velocity: int
    start: float
    stop: float

    def __init__(self, note, velocity, start, stop):
        self.note = note
        self.velocity = velocity
        self.start = start
        self.stop = stop
