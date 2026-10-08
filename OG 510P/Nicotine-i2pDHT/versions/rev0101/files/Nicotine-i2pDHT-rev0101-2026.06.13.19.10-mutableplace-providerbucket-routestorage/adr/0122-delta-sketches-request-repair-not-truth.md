# ADR 0122 — Delta sketches request repair, not truth

Accepted for rev0030.

Compact regional sketches are anti-entropy hints. They can request exact, child-range, or tombstone-first repair, but they must not become authoritative DHT truth.
