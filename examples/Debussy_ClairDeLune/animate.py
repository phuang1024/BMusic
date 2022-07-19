import bmusic
import bpy
import numpy as np
from math import sin, cos, hypot, radians

TREBLE_NOTE_COUNT = 46
TREBLE_PICK_COUNT = 8
BASS_NOTE_COUNT = 21
BASS_HAMMER_COUNT = 3

offset = 300
midi_treble = bmusic.Midi("/home/patrick/work/blender/piano/Debussy_ClairDeLune/audio/treble.mid", offset=offset)
midi_bass = bmusic.Midi("/home/patrick/work/blender/piano/Debussy_ClairDeLune/audio/bass.mid", offset=offset+2210)


def anim_treble_intensity():
    for i in range(TREBLE_NOTE_COUNT):
        obj = bpy.data.objects[f"treble.note.{i:03}"]
        anim = bmusic.Animator(obj, "pass_index", index=0)
        animkey = bmusic.AnimKey([anim], [0])
        animkey["on"] = [1000]
        mid = midi_treble.filter_notes([midi_treble.notes_used[i]])
        proc = bmusic.proc.IntensityFade(midi=mid, animkey=animkey, note_end=False, fade_fac=0.4)
        proc.animate()


def anim_treble_picks():
    # Scheduling
    animkeys = []
    for i in range(TREBLE_PICK_COUNT):
        obj = bpy.data.objects[f"treble.pick.{i:03}"]
        dist = np.interp(i, (0, TREBLE_PICK_COUNT-1), (0.35, 0.49))
        anim_lx = bmusic.Animator(obj, "location", index=0)
        anim_lz = bmusic.Animator(obj, "location", index=2)
        anim_ry = bmusic.Animator(obj, "rotation_euler", index=1)
        animkey = bmusic.AnimKey([anim_lx, anim_lz, anim_ry], [0, 2+dist, 0])
        for n in range(TREBLE_NOTE_COUNT):
            string = bpy.data.objects[f"treble.note.{n:03}"]
            ry = string.rotation_euler[1]
            lx = -dist * sin(ry)
            lz = -dist * cos(ry) + 2
            animkey[f"move{n}"] = [lx, lz, ry]
        animkeys.append(animkey)

    def cost_func(i, j):
        """Absolute distance between two notes."""
        str_i = bpy.data.objects[f"treble.note.{i:03}"]
        str_j = bpy.data.objects[f"treble.note.{j:03}"]
        rot_i = str_i.rotation_euler[1]
        rot_j = str_j.rotation_euler[1]
        pos_i = (sin(rot_i), cos(rot_i))
        pos_j = (sin(rot_j), cos(rot_j))
        diff = (pos_i[0] - pos_j[0], pos_i[1] - pos_j[1])
        dist = hypot(*diff)
        return 100 * dist

    proc = bmusic.proc.Scheduling(midi=midi_treble, depth=1, animkeys=animkeys, dist_f=cost_func)
    midis = proc.animate()
    
    # Hammer action
    for i in range(TREBLE_PICK_COUNT):
        obj = bpy.data.objects[f"treble.pick.{i:03}"]
        anim = bmusic.Animator(obj, "rotation_euler", index=2)
        animkey = bmusic.AnimKey([anim], [0])
        animkey["hit"] = [radians(40)]
        animkey["prepare"] = [radians(-40)]
        animkey["recoil"] = [radians(-30)]
        
        proc = bmusic.proc.Hammer(midi=midis[i], animkey=animkey)
        proc.animate()
        
    # Glowing with strings
    for i in range(TREBLE_PICK_COUNT):
        obj = bpy.data.objects[f"treble.pick.{i:03}"]
        anim = bmusic.Animator(obj, "pass_index", index=2)
        animkey = bmusic.AnimKey([anim], [0])
        animkey["on"] = [1000]
        
        proc = bmusic.proc.IntensityFade(midi=midis[i], animkey=animkey, note_end=False, fade_fac=0.3)
        proc.animate()
        
        
def anim_bass_intensity():
    # Glowing
    for i in range(BASS_NOTE_COUNT):
        obj = bpy.data.objects[f"bass.string.{i:03}"]
        anim = bmusic.Animator(obj, "pass_index", index=0)
        animkey = bmusic.AnimKey([anim], [0])
        animkey["on"] = [1000]
        mid = midi_bass.filter_notes([midi_bass.notes_used[i]])
        proc = bmusic.proc.IntensityFade(midi=mid, animkey=animkey, note_end=False, fade_fac=0.6)
        proc.animate()
        
    # Wobbling
    for i in range(BASS_NOTE_COUNT):
        obj = bpy.data.objects[f"bass.holder.{i:03}"]
        anim = bmusic.Animator(obj, "rotation_euler", index=1)
        animkey = bmusic.AnimKey([anim], [radians(-30)])
        animkey["on"] = [radians(-10)]
        mid = midi_bass.filter_notes([midi_bass.notes_used[i]])
        proc = bmusic.proc.IntensityWobble(midi=mid, animkey=animkey, note_end=False)
        proc.animate()
        
        
def anim_bass_hammers():
    # Scheduling
    animkeys = []
    for i in range(BASS_HAMMER_COUNT):
        obj = bpy.data.objects[f"bass.hammer_ctrl.{i:03}"]
        anim = bmusic.Animator(obj, "rotation_euler", index=2)
        animkey = bmusic.AnimKey([anim], [0])
        for n in range(BASS_NOTE_COUNT):
            animkey[f"move{n}"] = [radians(np.interp(n, (0, 20), (180, 0)))]
        animkeys.append(animkey)

    proc = bmusic.proc.Scheduling(midi=midi_bass, depth=4, animkeys=animkeys)
    midis = proc.animate()

    # Hammer action
    for i in range(BASS_HAMMER_COUNT):
        obj = bpy.data.objects[f"bass.hammer.{i:03}"]
        anim = bmusic.Animator(obj, "rotation_euler", index=1)
        animkey = bmusic.AnimKey([anim], [radians(0)])
        animkey["hit"] = [radians(45)]
        animkey["prepare"] = [radians(-60)]
        animkey["recoil"] = [radians(-30)]

        proc = bmusic.proc.Hammer(midi=midis[i], animkey=animkey, wobble_period=0.5, prepare_dur=0.2, hit_dur=0.1, recoil_dur=0.3)
        proc.animate()


anim_bass_intensity()
