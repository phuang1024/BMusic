.. _animator:

Animator
========

The :class:`~bmusic.Animator` class provides an interface to Blender's fcurve
animation API. This class does not add many features, but is easier to use.

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

We create an Animator object that operates on the object ``Cube``'s
``location[2]`` (Z location). We can then call the ``animate`` method to insert
keyframes. The arguments are
``(frame, value, handle="AUTO_CLAMPED", type="KEYFRAME")``.
