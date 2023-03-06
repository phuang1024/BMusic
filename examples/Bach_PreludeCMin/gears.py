import random

import bmusic
import bpy

FPS = bpy.context.scene.render.fps
TEMPO = 132
OFFSET = 60
FRAMES = 3000


def anim_gear(obj_name):
    obj = bpy.data.objects[obj_name]
    anim = bmusic.Animator(obj, "rotation_euler", 0)

    beat_time = 60 / TEMPO / 4 * FPS
    beat_time *= random.choice((2, 4, 8, 16))
    mult = random.choice((1, 2, 4, 8))
    step_size = random.uniform(0.1, 0.5)

    i = 0
    curr_pos = 0
    frame = OFFSET
    while frame < FRAMES:
        dir = (i // mult) % 2
        dir = 1 if dir == 0 else -1

        anim.animate(frame-6, curr_pos, type="BREAKDOWN")
        curr_pos += dir * step_size
        anim.animate(frame, curr_pos)

        i += 1
        frame += beat_time


for obj in bpy.data.objects:
    if "gear" in obj.name and "large" not in obj.name:
        anim_gear(obj.name)
