# SQLite WAL persistence and current runtime-risk note (rev0064)

Source: official SQLite Write-Ahead Logging documentation.
Accessed: 2026-06-18T02:33:00-04:00.
Evidence reference: turn103932view0 lines 84–109, 138–153, and 195–218.

Bounded observations used in P0003-D003:

- In WAL mode, original database content remains in the main file while committed changes can reside in the WAL until checkpoint.
- The WAL is part of persistent database state and must remain paired with the database when copied or moved.
- Current documentation describes a rare WAL-reset race affecting a broad runtime range and requiring concurrent connections that write or checkpoint at a tightly timed moment.
- The packaged builder reports SQLite 3.46.1, uses one build connection, disables automatic checkpointing, has no concurrent writer, and performs no checkpoint during the committed transition; therefore its recorded execution profile does not exercise the documented trigger.

This is a bounded compatibility and handling note. It does not prove that the runtime is generally risk-free, and it is not poem-quality evidence.

This snapshot is not a full source capture.
