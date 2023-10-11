MIDI
====

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

   # Only messages that play notes (60, 62, 64, 65)
   # These are MIDI notes; in this case, C4, D4, E4, F4.
   print(midi.filter_notes({60, 62, 64, 65}))

   # Iterate through all messages.
   for note in midi:
       print(note)

   # Split midi into tracks that each contain only one unique note.
   # Useful when each object in your scene only plays one note; for example, one hammer on a piano.
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
