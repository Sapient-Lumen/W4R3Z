# ADR 0092 — Range sketches request repair, not truth

Accepted for rev0023.

Compact regional roots are useful because exact-object comparison does not scale. They are dangerous if treated as truth. rev0023 therefore uses signed range sketches only to request exact repair, detect forks/stale replay, and prioritize tombstone repair.
