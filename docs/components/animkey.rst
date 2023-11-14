.. _animkey:

AnimKey
=======

The :class:`~bmusic.AnimKey` allow us to write **generalized algorithms**, while
users are able to **customize** the exact motion.


Quickstart
----------

.. code-block:: python

   import bmusic
   import bpy

   # Animator on X location
   anim1 = bmusic.Animator(bpy.context.object, "location", 0)
   # Z location
   anim2 = bmusic.Animator(bpy.context.object, "location", 2)

   # Define the animkey; basis is [0, 0]
   animkey = bmusic.AnimKey([anim1, anim2], [0, 0])
   # New "up" key
   animkey["up"] = [0, 1]
   # New "forward" key
   animkey["forward"] = [1, 0]

   # Animate at frame=0 at basis
   animkey.animate(0)
   # Animate at frame=30 with "up" key
   animkey.animate(30, up=1)
   # Animate at frame=60 with "forward" key
   animkey.animate(60, forward=1)
   # Animate at frame=90 with "up" and "forward" * -1
   animkey.animate(90, up=1, foward=-1, type="JITTER")


About
-----

Inspired by Blender's shape keys, AnimKeys perform the following functions:

- Controls multiple :class:`~bmusic.Animator` at once.
- Matches *keys* (human-readable and user-defined strings) to *values* for each
  animator.

Much like the animators, you can use the AnimKey to insert a single keyframe for
each animator at some frame, with the same control over handle and type.


Abstract example
^^^^^^^^^^^^^^^^

Let's say our system contains a hammer and a light. For each message, the hammer
should strike an object, and the light will turn on.

We have two :class:`~bmusic.Animator` objects: One for the hammer's rotation,
and one for the light's power.

We could define two keys in this situation: ``on`` would be when the message is
playing (light is on and hammer is striking), and ``off`` is the opposite.

So the AnimKey would, abstractly, look like this:

- Animators: ``Animator(hammer, rotation)``, ``Animator(light, power)``.
- ``on``: ``[45degrees, 100]`` (maps to hammer and light, respectively).
- ``off``: ``[0degrees, 0]``. In practice, this should be defined as the basis
  key (see below).


Factors and basis
^^^^^^^^^^^^^^^^^

The ``basis`` key --- conceptually, the default position --- is always required.
In the code, you provide it to the AnimKey constructor.

In the above example, the basis would be equivalent to ``off``.

In contrast to the animators where you provide the *value* to animate to, the
AnimKey takes *factors* (weights) for each key.

Then, after computing the final value for each animator based on the keys and
their factors, the AnimKey will insert the keyframes.

For example:

- Calling the AnimKey with no explicit factors results in the basis key.
- Setting a single key to 1 and the rest to 0 results in that key.

TODO


Using it
--------

Create the AnimKey:

- Define your Animators.
- Create the AnimKey.
- Define 

TODO
