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

   # Define the animkey; basis is [0, 0], values corresponding to respective animator.
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

AnimKeys map **abstract, generalized keys** (strings) to **specific,
user-defined values** to animate.

The animation algorithm (called a :class:`~bmusic.Procedure`) calls these
generalized keys, which the AnimKey converts to specific motions, using the
user-defined values.

Abstract example
^^^^^^^^^^^^^^^^

A simple OnOff algorithm could be defined as: **For each message, turn "on" when
it starts and turn "off" when it ends.**.

By changing the definitions of **on** and **off** in our AnimKey, we can change
the result without changing the algorithm itself.

Let's say our system contains a hammer and a light. For each message, the hammer
should strike an object, and the light will turn on.

We have two :class:`~bmusic.Animator` objects: One for the hammer's rotation,
and one for the light's power.

We define two keys in this situation: ``on`` would be when the message is
playing (light is on and hammer is striking), and ``off`` is the opposite.

So the AnimKey would look like this:

- Animators: ``Animator(hammer, rotation)``, ``Animator(light, power)``.
- ``on``: ``[45degrees, 100]`` (maps to hammer and light, respectively).
- ``off``: ``[0degrees, 0]``.

We then pass this AnimKey to the OnOff algorithm.

Notice how versatile the algorithm (OnOff) becomes: The user can change the
AnimKey to fit any OnOff situation, while the algorithm itself remains the same.

Factors and basis
^^^^^^^^^^^^^^^^^

In contrast to the animators where you provide the *value* to animate to, the
AnimKey takes *factors* (weights) for each key.

The resulting value (that is inserted as a keyframe) is a linear combination of
the keys, using the factors as weights.

Each AnimKey has a ``basis`` key --- conceptually, the default position. In the
code, you provide it to the AnimKey constructor.

In the above OnOff example, the basis should replace ``off`` (so there should be
two keys: ``basis`` and ``on``).

All keys are considered to be relative to the basis key. Therefore:

- Calling the AnimKey with no explicit factors results in the basis key.
- Setting a single key to 1 (e.g. ``on=1``) results in the ``on`` position.
- Setting ``on`` between 0 and 1 results in a corresponding transition between
  ``basis`` and ``on``.

Using it
--------

Steps to create an AnimKey:

- Define your Animators.
- Create the AnimKey and basis key.
- Define all other keys.

.. code-block:: python

   import bmusic
   import bpy

   # Define animators
   # Hammer rotation
   anim1 = bmusic.Animator(obj1, "rotation_euler", 0)
   # Light power
   anim2 = bmusic.Animator(obj2.data, "energy")

   # Create AnimKey with the basis key
   basis = bmusic.AnimKey([anim1, anim2], [0, 0])

   # Define other keys
   basis["up"] = [radians(45), 100]

   # Animate
   basis.animate(0)  # Frame=0; basis
   basis.animate(30, up=1)  # Frame=30; hammer striking and light on
   basis.animate(60, up=0.5)  # Frame=60; hammer halfway and light halfway on

Provide the key values as **absolute** values.

Even though they are converted to be relative to the basis internally, the user
provides the absolute values.

In this example, this means that regardless of what the basis is, you provide
the position the hammer should rotate to and the power the light should shine
at.
