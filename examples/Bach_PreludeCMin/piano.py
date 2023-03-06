import math

import bmusic
import bpy

midi = bmusic.Midi(bpy.path.abspath("//Audio/robotic.mid"), offset=60)


def anim_hammers():
    notes_used = sorted(midi.notes_used, reverse=True)
    for i in range(len(notes_used)):
        mid = midi.filter_notes([notes_used[i]])
        obj = bpy.data.objects[f"hammer.{i:03d}"]
        anim = bmusic.Animator(obj, "rotation_euler", 0)
        animkey = bmusic.AnimKey([anim], [math.radians(15)])
        animkey["hit"] = [0]
        animkey["prepare"] = [math.radians(60)]
        animkey["recoil"] = [math.radians(60)]
        proc = bmusic.proc.Hammer(midi=mid, animkey=animkey)
        proc.animate()

        led = bpy.data.objects[f"led_green.{i:03d}"]
        anim = bmusic.Animator(led, "pass_index")
        animkey = bmusic.AnimKey([anim], [0])
        animkey["on"] = [200]
        proc = bmusic.proc.IntensityOnOff(midi=mid, animkey=animkey, duration=0.03)
        proc.animate()


anim_hammers()
