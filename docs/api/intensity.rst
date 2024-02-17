Intensity
=========

The Intensity procedures deal with a single scalar intensity.

As a result, they are very versatile: The value can be mapped to the power of a
light, the rotation of a hammer, the press of a key, etc.


Intensity base class
--------------------

The :class:`Intensity` base class defines common parameters, but does not
implement any animation.

The ``min_intensity`` and ``max_intensity`` parameters linearly curve MIDI
velocities to their corresponding intensity.

For example, setting ``min_intensity=0.5`` and ``max_intensity=1.0`` will map
MIDI velocities ``(0, 127)`` to intensities ``(0.5, 1.0)``.


IntensityOnOff
--------------

The :class:`IntensityOnOff` class turns on when a message starts, and turns off
when it ends.

The intensity turns on at the time the message starts; that is, it begins
transitioning to on a bit before that time.

Similarly, it stays on until the message ends, and then transitions to off a bit
after that time.

The magnitude to which it turns on is determined by ``min_intensity``,
``max_intensity``, and the MIDI velocity.

Set the ``duration`` parameter to the time spent transitioning between states.

.. code-block:: py

   IntensityOnOff(
       midi=midi,
       animkey=animkey,
   )

   IntensityOnOff(
       ...
       duration=0.1,
   )


IntensityFade
-------------

The :class:`IntensityFade` class transitions to the peak intensity when a
message starts, and fades gradually over time.

Actually, IntensityFade is very versatile. It can do much more than fade out.
More about this later.

The default configuration uses an exponential decay.

Customize the falloff by assigning ``fade_func``, a function that takes in time
in seconds since the note started and returns a multiplicative factor.

.. code-block:: py

   IntensityFade(
       midi=midi,
       animkey=animkey,
   )

   # Customize with builtin interpolation.

   exp_factor = 0.5
   IntensityFade(
       ...
       fade_func=lambda t: bmusic.utils.EXPONENTIAL(exp_factor, t),
   )

   lin_factor = 0.5
   IntensityFade(
       ...
       fade_func=lambda t: bmusic.utils.LINEAR(lin_factor, t),
   )

IntensityFade has features to prevent unnecessary keyframing on every frame:

- ``key_interval``: The interval in frames between keyframes. Often, Blender's
  interpolation is good enough to not need a keyframe on every frame.
- ``off_thres``: When the intensity falls below this value, the animation is
  turned off. This is useful to prevent unnecessary keyframing when the
  intensity is very low.
- ``max_len``: The maximum length of the animation. This is useful to prevent
  the animation from running indefinitely.

----

Customizing ``fade_func`` makes it possible to create a variety of effects.

If your ``fade_func`` is not monotonic decreasing, make sure to set
``off_thres`` to a negative value, to prevent the procedure from cutting off
the animation at an inappropriate time.

For example, combining ``EXPONENTIAL`` and ``OSCILLATE`` creates an oscillation
that decays.

.. code-block:: py

   IntensityFade(
       ...
       fade_func=lambda t: bmusic.utils.EXPONENTIAL(0.5, t) * bmusic.utils.OSCILLATE(0.3, t),
       off_thres=-1,
   )
