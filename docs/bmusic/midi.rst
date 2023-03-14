MIDI
====

Basic MIDI processing
---------------------

BMusic uses ``mido`` to parse MIDI files.

BMusic implements two classes to represent MIDI data:

- :class:`bmusic.MessageList` is a single track of messages.
- :class:`bmusic.Message` is a single message containing absolute
  frame start and end times.

.. code-block:: python

   import bmusic

   # Offset is frame timestamp the first message starts at.
   # Here, first message starts at frame 10.
   midi = bmusic.parse_midi("/path/to/midi.mid", offset=10)

   # Alternatively, construct empty track
   midi2 = bmusic.MessageList()
   # or from a list of messages.
   midi3 = bmusic.MessageList([...])

   # Total duration in frames.
   print(midi.duration())

   # Only notes (10, 11, 12)
   print(midi.filter_notes({10, 11, 12}))

   # Iterate through all messages.
   for note in midi:
       print(note)

   # Split midi into tracks that each contain only one note.
   for track in midi.split_notes():
       print(f"This track has {len(track)} messages of the note {track[0].note}.")

   # Linked list behavior.
   first_msg = midi[0]
   second_msg = first.next()
   first_msg_again = second_msg.prev()

   # Create single message
   note = 40
   velocity = 100
   start = 10
   end = 20
   msg = bmusic.Message(note, velocity, start, end)


Affixes
-------

BMusic also has utilities to compute *affixes* for each message in a track,
described below.

What are affixes?
^^^^^^^^^^^^^^^^^

Most of the time in animations, we animate many frames around a message's frame.
For example, a hammer may anticipate the hit by moving back *before* the hit,
and recoil *after*.

For a single message, this is simple: Just hard-code the movements and animate
them.

But, if we have many messages close to each other, the keyframes may overlap: There
might not be enough time for the hammer to recoil and anticipate completely.

The solution is to check the proximity of the messages immediately before and after
our current message. We then adjust (e.g. shorten the motion) to avoid the overlap.

This is common enough that BMusic provides tools to compute how much time there is
before and after each message.

These are called *affixes*: The *prefix* is the time before, and the *suffix* is after.

BMusic utilities
^^^^^^^^^^^^^^^^

.. code-block:: python

   affixes = bmusic.compute_affixes(midi)
   for msg in affixes:
       # msg is an AffixMessage, which is a subclass of Message.
       print(msg)
       print("Prefix:", msg.prefix)
       print("Suffix:", msg.suffix)

For more on using affixes, see the tutorial section.
