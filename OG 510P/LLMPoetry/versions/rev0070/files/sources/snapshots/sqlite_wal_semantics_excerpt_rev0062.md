# SQLite WAL semantics — selected excerpt notes (rev0062)

Source: official SQLite documentation, `https://sqlite.org/wal.html`.
Captured: 2026-06-18T00:02:00-04:00.
Evidence reference: turn779592view0.

Selected, paraphrased points used in P0003-D001:

- WAL mode leaves original pages in the database while subsequent changes are appended to a separate write-ahead log.
- A transaction becomes committed when its commit record is appended to the WAL.
- Checkpointing transfers WAL transactions back into the database.
- The WAL is part of persistent database state and must remain with the database when copying or moving it; separating the files can lose committed transactions or damage state.

This is not a full capture and not complete documentation. It is a bounded source excerpt for traceability, not poem-quality evidence.
