# SQLite database/journal separation hazard — selected notes (rev0063)

Source: official SQLite “How To Corrupt An SQLite Database File” documentation.
Accessed: 2026-06-18T00:31:00-04:00.
Evidence reference: turn369389view0.

Selected bounded observation used in the D002 artifact contract:

- A database and the journal state describing its transaction must be treated as one stateful unit.
- Copying or moving one without the other can discard committed changes or leave an invalid combination.

This is not a full capture of the documentation. It supports artifact handling only, not poem quality.
