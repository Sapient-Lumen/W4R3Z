# ADR 0086 — repair-market replay memory before garden selection

Accepted for rev0021.

A garden repair offer is local capacity evidence for one window.  Reusing the same offer digest, rolling a sequence backward, or repeatedly selecting one family across windows is a capture surface.  `repairreplay.py` makes that pressure explicit.
