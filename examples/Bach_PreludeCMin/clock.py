import math
import random

import bmusic
import bpy

pi = math.pi

# Frames
OFFSET = 60
FPS = bpy.context.scene.render.fps

# --- Clock settings
# bpm
TEMPO = 132
FRAMES = 3000
# per half rot
ROT_TIME = 0.1 * FPS
# degrees
OVERSHOOT = math.radians(15)
WOBBLE_PERIOD = 0.16 * FPS
WOBBLE_DECAY = 0.8
WOBBLE_COUNT = 6


def anim_clock():
    secs_per_beat = 60 / TEMPO

    for i in range(10):
        digit = bpy.data.objects[f"digit.{i:03d}"]
        led = bpy.data.objects[f"led.{i:03d}"]
        anim_digit = bmusic.Animator(digit, "rotation_euler", 0)
        anim_led = bmusic.Animator(led, "pass_index")

        wobble_period = random.uniform(0.9, 1.1) * WOBBLE_PERIOD
        tick_time = secs_per_beat * 2 ** (i-2) * FPS
        do_wobble = tick_time > ROT_TIME + wobble_period
        if do_wobble:
            wobble_count = int((tick_time - ROT_TIME) / wobble_period)

        # actually half revs
        revs = 0
        frame = OFFSET
        while frame < FRAMES + OFFSET:
            # --- Rotation
            # If do wobble, we need to zero the overshoot
            # Else, it would have been done by prev iteration.
            if revs == 0:
                anim_digit.animate(frame, pi*revs, type="EXTREME")

            revs += 1
            frame += tick_time
            if do_wobble:
                # Previous position
                anim_digit.animate(frame-ROT_TIME, pi*(revs-1), type="BREAKDOWN", handle="VECTOR")

                # Wobble
                for j in range(wobble_count):
                    curr_frame = frame + j * wobble_period
                    wobble = OVERSHOOT * WOBBLE_DECAY ** j * (1 if j % 2 == 0 else -1)
                    anim_digit.animate(curr_frame, pi*revs + wobble, type="JITTER")
            else:
                # Go directly to next rot
                anim_digit.animate(frame, pi*revs, type="EXTREME", handle="VECTOR")

            # --- LED
            prev, now = 0, 100
            if revs % 2 == 0:
                prev, now = now, prev
            anim_led.animate(frame-1, prev, type="BREAKDOWN")
            anim_led.animate(frame, now)


anim_clock()
