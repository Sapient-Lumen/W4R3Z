# ADR 0140 — start profile matrix before live launch

Status: accepted for the design cube.

A future DHT node must not launch merely because component reports passed.  It launches under a profile: leaf, garden, bridge, or offline design.  Each profile has different service, metadata, and router requirements.

rev0035 adds `startmatrix.py` to make those requirements explicit and testable before live transport exists.
