Procedures
==========

:class:`~bmusic.proc.Procedure` classes define animation algorithms, making use of :class:`~bmusic.AnimKey` objects.
Because of the versatility of AnimKeys, Procedures can be very general. For example, a Procedure might be defined as
``animate to key "up" when playing and "down" when not playing``. The user can then define what ``up`` and ``down``
mean via the AnimKey.

Procedures should extend the Procedure base class. Every procedure has *parameters*, which are provided with keyword
arguments in the constructor. Subclasses inherit available parameters from their parent class.

If you would like to learn how to create your own Procedure, please see TODO. This page describes how to use procedures.

Example
-------

This example uses the :class:`~bmusic.proc.IntensityOnOff` procedure, which turns on when a note plays and off when
it stops.

.. code-block:: python

   import bpy
   import bmusic

   obj = bpy.context.object

   anim = bmusic.Animator(obj, "location", 2)
   animkey = bmusic.AnimKey([anim], [0])
   # This key is required by the procedure (see docs).
   animkey["on"] = [1]

   midi = bmusic.Midi("/path/to/midi.mid", offset=30)

   # See docs for available parameters.
   proc = bmusic.proc.IntensityOnOff(midi=mid, animkey=animkey, duration=0.2)
   proc.animate()
