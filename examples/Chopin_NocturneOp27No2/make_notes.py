import bpy
import numpy as np

NUM_NOTES = 65

# Very bottom to very top
MAX_LEN = 1.55
MIN_LEN = 0.5

# Length of respective parts
BOTTOM_LEN = 0.05
TOP_LEN = 0.1

# Bounds of custom properties of string_driver
MAX_SCALE = (1, 0.5)
ROT_SPEED = (60, 200)


def scale_notes():
    scale_fac = (MIN_LEN / MAX_LEN) ** (1 / NUM_NOTES)
    str_init_len = MAX_LEN - BOTTOM_LEN - TOP_LEN
    for note in range(NUM_NOTES):
        length = MAX_LEN * scale_fac ** note
        str_len = length - BOTTOM_LEN - TOP_LEN
        str_scale = str_len / str_init_len
        delta = MAX_LEN - length

        objs = bpy.data.objects
        empty = objs[f"note.{note:03}"]
        top = objs[f"top.{note:03}"]
        string = objs[f"string.{note:03}"]
        driver = objs[f"string_driver.{note:03}"]

        empty.location[2] += delta / 2
        top.location[2] -= delta
        driver.scale[2] = str_scale
        string.modifiers["Array"].fit_length = str_len + 0.05
        string.scale[0] = string.scale[1] = np.interp(note, (0, NUM_NOTES-1), (1, 0.4))

        driver["max_scale"] = np.interp(note, (0, NUM_NOTES-1), MAX_SCALE)
        driver["rot_speed"] = np.interp(note, (0, NUM_NOTES-1), ROT_SPEED)
        

def link_mesh(name):
    for obj in bpy.data.objects:
        if obj.name.startswith(f"{name}."):
            obj.data = bpy.data.meshes[name]



scale_notes()
for n in ("top", "bottom", "string"):
    link_mesh(n)
