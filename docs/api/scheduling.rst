Scheduling
==========


Algorithm
---------

There are two rules:

1. Hammers remain in their "zones".
     If there are e.g. 4 hammers, each hammer should, if possible, play their
     share of 25% of the notes.

2. Rule 1 can be broken to "alleviate" a large workload in a zone.
     If one zone has a lot of notes in the short term (e.g. a trill), other
     hammers can play these notes.

Rule 1 implementation
^^^^^^^^^^^^^^^^^^^^^

Rule 1 is implemented with a histogram of the near future.

The distribution of upcoming notes (up to a predefined lookahead) is created.
This is split into N zones, where each zone has an equal (or roughly equal)
cumulative sum of the distribution.

This is sufficient for slow playing: The zone and hammer that corresponds to the
message is the one that plays.

To merge this with Rule 2, we also define a cost with respect to Rule 1.

A hammer playing within it's zone has cost 0.
The cost increases the further away from the zone the hammer is.

Rule 2 implementation
^^^^^^^^^^^^^^^^^^^^^

This is a greedy algorithm.

For the current message, we compute the cost of each hammer taking this message
(given it's current position and when it last played).

Choose the hammer with the lowest cost.

- We can calculate the *velocity* the hammer needs to move to reach the message
  in time --- ``distance / time``.
- Distance is euclidian distance, but could be overriden with a custom metric.
- Time is duration between when the hammer last played and the current message.
