# SQLite WAL persistence and runtime boundary — bounded documentation note (rev0065)

Source: official SQLite documentation, *Write-Ahead Logging*.
Accessed: 2026-06-18T04:34:00-04:00.
Evidence references: turn515699view1 lines 132–153; turn515699view0 lines 195–218.

Bounded observations used in P0003-D004:

- SQLite describes the WAL as part of the database's persistent state and warns that separating it from the database can lose committed transactions or damage the database.
- Current documentation places SQLite 3.46.1 within the likely affected range for the rare WAL-reset bug.
- The documented trigger requires at least two connections and simultaneous write/checkpoint activity. D004's receipt records one connection, no concurrent writer, automatic checkpointing disabled, and no checkpoint during the committed transition.

This note records handling and compatibility boundaries only; it is not a guarantee for other runtimes or workloads and not literary evidence.
