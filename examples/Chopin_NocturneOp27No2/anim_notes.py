import os

import animpiano
import bpy
import mido
import numpy as np
from tqdm import trange

MIDI_PATH = os.path.expanduser("~/l/animpiano/Chopin_NocturneOp27No2/audio/midi.mid")

ANIM_OFFSET = 300   # Frames


def anim_play(note_i, play, frame):
    ctrl = bpy.data.objects[f"note.{note_i:03}"]
    string = bpy.data.objects[f"string.{note_i:03}"]
    ctrl["play"] = float(play)
    string.pass_index = int(play * 100)
    ctrl.keyframe_insert(data_path='["play"]', frame=frame)
    string.keyframe_insert(data_path="pass_index", frame=frame)


def get_play_values(notes, note):
    """
    Yields many values. Each value is (frame, play) meant to be keyframed.

    :param notes: List of parsed midi notes.
    :param note: Which note to compute?
    """
    decay_on = np.interp(note, (0, 64), (0.983, 0.97))

    notes = list(filter(lambda n: n.note == note, notes))
    starts = [(n.start, n.velocity) for n in notes]
    ends = [n.end for n in notes]
    starts.sort(key=lambda x: x[0], reverse=True)
    ends.sort(reverse=True)

    end_frame = max(starts[0][0], ends[0]) + 300

    playing = False
    play = 0
    for frame in range(0, int(end_frame)):
        if starts and frame >= starts[-1][0]:
            play = np.interp(starts[-1][1], (0, 128), (0, 1))
            playing = True
            starts.pop()

        if ends and frame >= ends[-1]:
            playing = False
            ends.pop()

        play *= decay_on if playing else 0.2

        rounded = int(play*1000) / 1000
        yield (frame, rounded)


def clean_keys1(keys, diff_thres=0.08, frame_thres=10):
    """
    Keys from get_play_values are for each frame.
    This function reduces keyframes to one per few frames.
    """
    last_keyed = last = next(keys)
    yield last

    try:
        while True:
            prox = next(keys)   # prox for "proximo", spanish "next"

            if abs(prox[1] - last[1]) >= diff_thres:
                # Big immediate change, key both before and after.
                yield last
                yield prox
                last_keyed = prox

            elif abs(prox[1] - last_keyed[1]) >= diff_thres:
                # Small gradual change, key intermediate frames.
                yield prox
                last_keyed = prox

            elif prox[0] - last_keyed[0] >= frame_thres:
                # Key once in a while.
                yield prox
                last_keyed = prox

            last = prox

    except StopIteration:
        pass


def clean_keys2(keys):
    """
    Clean keyframes.
    This function removes unnecessary intermediate keyframes in a long run of the same keys.
    """
    last = None
    curr = next(keys)

    try:
        while True:
            prox = next(keys)

            good = True
            if last is not None:
                if last[1] == curr[1] == prox[1]:
                    good = False

            if good:
                yield curr

            last = curr
            curr = prox

    except StopIteration:
        pass


def main():
    notes = animpiano.parse_midi(mido.MidiFile(MIDI_PATH), bpy.context.scene.render.fps)
    keys = sorted(animpiano.notes_used(notes))
    duration = max(n.end for n in notes)

    count = 0
    for i in trange(len(keys), desc="Play values"):
        note = keys[i]
        keyframes = clean_keys2(clean_keys1(get_play_values(notes, note)))
        for frame, play in keyframes:
            anim_play(i, play, frame+ANIM_OFFSET)
            count += 1
    print(f"Play values: {count} keyframes inserted.")


if __name__ == "__main__":
    main()
