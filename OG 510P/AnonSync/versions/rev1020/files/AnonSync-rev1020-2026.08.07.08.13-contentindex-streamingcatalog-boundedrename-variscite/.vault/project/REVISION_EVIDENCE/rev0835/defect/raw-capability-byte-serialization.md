# Defect: capability object representation crossed a pipe

## Before

A lineage test treated the raw bytes of a deliberately non-trivially-copyable
`SyncProcessIncarnation` object as transport evidence. That coupled the test to
object representation while the type intentionally prevents bitwise authority
construction.

## Correction

The child exports a fixed-layout trivially-copyable observation containing only
kernel PID and lineage generation. The parent verifies those facts; no
capability representation is serialized.
