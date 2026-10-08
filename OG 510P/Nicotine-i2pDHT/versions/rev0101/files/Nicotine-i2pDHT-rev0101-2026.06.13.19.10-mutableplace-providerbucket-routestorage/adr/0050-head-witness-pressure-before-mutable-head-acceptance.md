# ADR 0050 — Head witness pressure before mutable-head acceptance

Accepted for rev0013.

A valid mutable head is only an observation. Accepting it requires local monotonic memory, path-family diversity, and fork/stale/previous-link pressure handling.

Garden witnesses produce evidence. They do not produce truth.
