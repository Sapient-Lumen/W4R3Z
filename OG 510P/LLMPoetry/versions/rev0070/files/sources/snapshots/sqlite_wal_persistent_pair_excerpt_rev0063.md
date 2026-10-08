# SQLite WAL persistent-pair requirement — selected notes (rev0063)

Source: official SQLite Write-Ahead Logging documentation.
Accessed: 2026-06-18T00:31:00-04:00.
Evidence reference: turn369389view3.

Selected bounded observation used in the D002 artifact contract:

- A WAL file is part of persistent database state and should stay with its database when copied or moved.
- Read-only WAL inspection has filesystem conditions, so LLMPoetry reads disposable copies and verifies their persistent-byte hashes before and after inspection.

This is not a full capture of the documentation. It supports artifact handling only, not poem quality.
