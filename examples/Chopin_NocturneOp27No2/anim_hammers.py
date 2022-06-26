import os
from math import sin, cos, radians

import animpiano
import bpy
import mido
import numpy as np
from tqdm import trange

MIDI_PATH = os.path.expanduser("~/l/animpiano/Chopin_NocturneOp27No2/audio/midi.mid")

ANIM_OFFSET = 300   # Frames

# Currently, difficult to set keyframe handle type to vector.
# Solution: Manually change this value to True (only hit keys have vector handles),
# run script, change to vector from UI.
# Then, set this to False and run again.
ONLY_HIT_KEYS = False


def anim_hammer(note_i, frame, rot, x_loc, z_loc):
    """
    location params are delta from default.
    """
    hammer = bpy.data.objects[f"hammer.{note_i:03}"]
    ctrl = bpy.data.objects[f"note.{note_i:03}"]
    
    hammer.rotation_euler[1] = rot
    
    angle = np.interp(note_i, (0, 64), (0, 180))
    """
    hammer.location = (
        -1.87 * cos(angle),
        1.87 * sin(angle),
        0.4 + ctrl.location[2],
    )
    """

    #hammer.keyframe_insert(data_path="location", frame=frame)
    hammer.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    
def get_keys(notes, note):
    """
    Returns many (frame, rot_y) values to keyframe.
    """
    hits = sorted(((n.start, n.velocity) for n in filter(lambda n: n.note == note, notes)), key=lambda x: x[0])
    
    for i, (hit, vel) in enumerate(hits):
        prev = hits[i-1][0] if i > 0 else -1e9
        next = hits[i+1][0] if i < len(hits)-1 else 1e9

        hit_angle = np.interp(vel, (0, 128), (30, 70))
        
        if ONLY_HIT_KEYS:
            yield (hit, radians(-5.8))
        else:
            # Before hit
            if hit - prev > 180 + 17:
                yield (hit-17, 0)
            prepare = max(hit-5, (hit+prev) / 2)
            yield (prepare, radians(hit_angle))

            # After hit
            limit = min(160, next-hit-10)
            offset = 13
            last = [radians(hit_angle * 0.6), radians(-5)]
            i = 0
            while offset < limit:
                yield (hit+offset, last[i])
                last[i] *= 0.35
                offset += 20
                i = (i+1) % 2

            if next - hit > 200:
                yield (hit+offset, 0)


def main():
    notes = animpiano.parse_midi(mido.MidiFile(MIDI_PATH), bpy.context.scene.render.fps)
    keys = sorted(animpiano.notes_used(notes))
    duration = max(n.end for n in notes)

    for i in trange(len(keys), desc="Hammers"):
        note = keys[i]

        for frame, rot in get_keys(notes, note):
            anim_hammer(i, frame+300, rot, 0, 0)


if __name__ == "__main__":
    main()
