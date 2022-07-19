MIDI
====

BMusic has a class :class:`~bmusic.Midi` which uses ``mido`` internally. It provides absolute frame timestamps
for each :class:`~bmusic.Note` and simple linked-list like behavior.

.. code-block:: python

   import bmusic

   # Offset is frame timestamp the first note will start at.
   # In this case, first note starts at frame 10.
   midi = bmusic.Midi("/path/to/midi.mid", offset=10)

   # Alternatively, construct from a list of notes.
   midi2 = bmusic.Midi.from_notes([...])

   # Total length in frames.
   print(midi.length)

   # Only notes (10, 11, 12)
   print(midi.filter_notes({10, 11, 12}))

   # Iterate.
   for note in midi:
       print(note)

   # Linked list behavior.
   first_note = midi.notes[0]
   second_note = first.next
   first_note_again = second_note.prev
