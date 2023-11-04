.. _animator:

Animator
========


Quickstart
----------

.. code-block:: python

   import bmusic
   import bpy

   obj = bpy.context.object   # Make sure Cube is the active obj
   animator = bmusic.Animator(obj, "location", 2)
   animator.animate(frame=0, value=0)
   animator.animate(30, 1, handle="VECTOR")
   animator.animate(60, 0, type="EXTREME")


About
-----

The :class:`~bmusic.Animator` class provides an interface to Blender's fcurve
animation API.

This class does not add many features, but is easier to use.


Keyframes
---------

Blender uses
`Keyframes <https://docs.blender.org/manual/en/latest/animation/keyframes/index.html>`_
to do animation.

Keyframes can be loosely thought of as containing:

- Frame: When in time the keyframe is.
- Value: The value of the property (e.g. location) at that frame.
- Handle: How the curve is interpolated between this keyframe and the next.
- Type: An organizational tag for the keyframe.


Handle
^^^^^^

Blender will automatically interpolate between keyframes. For example, if you
have two keyframes on frames 0 and 100, the value will smoothly transition from
the first to the second over the course of the 100 frames.

In Blender's Graph Editor, you can edit keyframes as bezier curves, allowing
very fine control over the interpolation.

In BMusic, however, we only change the keyframe handle type. Naturally, this
restricts the amount of control we have over the interpolation.

The two most common handle types are ``AUTO_CLAMPED`` and ``VECTOR``.

.. image:: ./KeysAutoClamped.jpg

``AUTO_CLAMPED`` is the default. It will smoothly transition between the
previous and next keyframes, speeding up in the middle and slowing down at the
edges.

.. image:: ./KeysVector.jpg

``VECTOR`` will have a sharp stop and start around the keyframe. This is useful
when you're animating a sharp motion, such as when a hammer strikes the strings.


Type
^^^^

The type is an organizational tag for the keyframe.

.. image:: ./KeysTypes.jpg

The five types are:

- ``KEYFRAME``: Yellow. The default type.
- ``BREAKDOWN``: Blue and small.
- ``MOVING_HOLD``: Looks like ``KEYFRAME``.
- ``EXTREME``: Red and large.
- ``JITTER``: Green and small.

Again, these are purely organizational; they don't change the functionality of
anything.

BMusic will set the types to make it easier to see what's going on. For example,
each keyframe corresponding to the hammer striking will be ``EXTREME``.


BMusic API
----------

An Animator controls a single fcurve of an object.

To create the Animator, first define:

- The object to animate.
- The fcurve *name*. For example, ``location``, ``rotation_euler``, ``scale``,
  ``pass_index``.
- Optionally, the fcurve *index*. For example, ``0`` for X, ``1`` for Y, ``2``
  for Z.

Then, create the Animator:

.. code-block:: python

   animator = bmusic.Animator(obj, name, index)
   # or
   animator = bmusic.Animator(obj, name)

   # Examples
   animator = bmusic.Animator(bpy.context.object, "rotation_euler", 2)
   animator = bmusic.Animator(bpy.data.objects["Object"], "pass_index")

Call the ``animate()`` method to insert a keyframe:

.. code-block:: python

   # Signature
   animator.animate(frame, value, handle="AUTO_CLAMPED", type="KEYFRAME")

   # Examples
   animator.animate(0, 0)
   animator.animate(30, 1, handle="VECTOR")
   animator.animate(60, 0, type="EXTREME")
