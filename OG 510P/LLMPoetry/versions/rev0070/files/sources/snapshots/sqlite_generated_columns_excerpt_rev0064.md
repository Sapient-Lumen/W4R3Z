# SQLite generated columns — VIRTUAL read-time computation (rev0064)

Source: official SQLite Generated Columns documentation.
Accessed: 2026-06-18T02:33:00-04:00.
Evidence reference: turn685308view3 lines 38–65 and 89–95.

Bounded observations used in P0003-D003:

- A generated column’s value is a function of other columns in its row and cannot be written directly.
- A VIRTUAL generated column is computed when read.
- Generated-column support begins with SQLite 3.31.0; older readers do not understand schemas using the feature.

D003 uses a VIRTUAL generated column for vacancy classification and records that compatibility floor. This supports formal behavior only.

This snapshot is not a full source capture.
