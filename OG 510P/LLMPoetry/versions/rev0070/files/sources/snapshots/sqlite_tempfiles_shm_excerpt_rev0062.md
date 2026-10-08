# SQLite WAL/SHM temporary-file semantics — selected excerpt notes (rev0062)

Source: official SQLite documentation, `https://sqlite.org/tempfiles.html`.
Captured: 2026-06-18T00:02:00-04:00.
Evidence reference: turn779592view1.

Selected, paraphrased points used in P0003-D001:

- WAL sidecars conventionally use the database filename plus the `-wal` suffix.
- The `-shm` shared-memory file does not contain persistent content and can be reconstructed from the WAL.

This is not a full capture and not complete documentation. It is a bounded source excerpt for traceability, not poem-quality evidence.
