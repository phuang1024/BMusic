Animator
========

The :class:`~bmusic.Animator` class provides an interface to Blender's fcurve animation API.
This class does not add many features, but is easier to use.

Example
-------

Run this in the default Blender file.

.. code-block:: python

   import bmusic
   import bpy

   obj = bpy.context.object   # Make sure Cube is the active obj
   animator = bmusic.Animator(obj, "location", 2)
   animator.animate(0, 0)
   animator.animate(30, 1, handle="VECTOR")
   animator.animate(60, 0, type="EXTREME")

We create an Animator object that operates on the object ``Cube``'s ``location[2]`` (Z location).
We can then call the ``animate`` method to insert keyframes. The arguments are
``(frame, value, handle="AUTO_CLAMPED", type="KEYFRAME")``.


AnimKey
=======

The :class:`~bmusic.AnimKey` class groups abstract named positions with their respective shapes
for animation, inspired by Blender's Shape Key feature.

For example, an ``on`` position may be setting a light's power to ``100``, or a ``hit`` position
may be setting a hammer's rotation to ``10``.

AnimKeys allow us to write generalized algorithms while users are able to customize the exact motion.

For example, our algorithm may contain

.. code-block::

   for each note:
       animate_hit(note)

What does a "hit" do? The user defines it to fit their needs. All our algorithm needs to do is
perform a "hit".

Example
-------

.. code-block:: python

   import bmusic
   import bpy

   # Animator on X location
   anim1 = bmusic.Animator(bpy.context.object, "location", 0)
   # Z location
   anim2 = bmusic.Animator(bpy.context.object, "location", 2)

   animkey = bmusic.AnimKey([anim1, anim2], [0, 0])
   animkey["up"] = [0, 1]
   animkey["forward"] = [1, 0]

   animkey.animate(0)
   animkey.animate(30, up=1)
   animkey.animate(60, forward=1)
   animkey.animate(90, up=1, foward=-1, type="JITTER")

AnimKeys control multiple animators at once. In this case, we created animators for the cube's X
and Z location.

The AnimKey object has many *keys*, each of which is a sequence of numbers, one for each animator.
For example, a key of ``[10, 20]`` means that the first animator will animate to ``10``, and the
second animator will animate to ``20``.

When initializing the AnimKey, we always provide the ``basis`` key which can be thought of as the
resting or default position. In this case, the basis is ``[0, 0]``, where the X and Z are both 0.

Next, we can define more keys. The ``up`` key sets Z to ``1``, and ``forward`` sets X to ``1``.

Last, we can call the ``animate`` method. The first argument is the frame. Other keyword arguments are
the strengths of each key. We can combine keys, and strengths are not limited to ``(0, 1)``. The
parameters ``type`` and ``handle`` are also available.

Keys are converted to diffs internally. That is, the AnimKey stores the difference between the
key and the basis. In this case, because the basis is ``[0, 0]``, the key is unchanged. Because
the keys are diffs, we can interpret them to mean *offsets* from the basis. For example, the
``up`` key means that the Z location will be increased by ``1``. In practice you don't need to
worry about this. Just remember to provide **absolute** (not relative) values to the AnimKey, which
will be converted automatically.

When calling ``animate`` with strengths, the AnimKey will start with the basis, and add the diffs
of each key. The key values are linearlly interpolated between strength ``(0, 1)``.
