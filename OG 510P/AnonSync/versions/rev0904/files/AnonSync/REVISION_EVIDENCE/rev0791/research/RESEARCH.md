# rev0791 research notes

Primary sources were deliberately limited to official SQLite documentation.

## Referential integrity is a separate restart proof

SQLite explicitly states that `PRAGMA integrity_check` does **not** find foreign
key errors and directs applications to `PRAGMA foreign_key_check`. The latter
returns one row for each violated foreign-key constraint. Enabling
`PRAGMA foreign_keys=ON` controls enforcement of subsequent statements; it is
not a retrospective proof that pre-existing rows satisfy the relationships.

Sources:

- https://sqlite.org/pragma.html#pragma_integrity_check
- https://sqlite.org/pragma.html#pragma_foreign_key_check
- https://sqlite.org/pragma.html#pragma_foreign_keys

## Declared constraints are not read-time semantic authority

SQLite documents that constraints are generally checked on writes and that a
query can return values violating declared constraints when a file has been
modified or corrupted. Therefore AnonSync must verify exact storage classes,
bytes, ranges, grammar, cross-row uniqueness, and protocol relationships while
reconstructing restart authority; schema declarations alone are insufficient.

Source: https://sqlite.org/lang_createtable.html#constraint_enforcement

## Resource containment remains unfinished

SQLite's untrusted-input guidance recommends defensive mode, substantially
reduced runtime limits, progress/interrupt budgets, a hard heap limit,
`trusted_schema=OFF`, early integrity checking, `cell_size_check=ON`, and
`mmap_size=0`. Rev0791 adds per-field replay-row byte ceilings but does not yet
bound total database size, total rows, total VDBE work, wall time, or total
SQLite heap. Those remain a separate release-level resource profile.

Sources:

- https://sqlite.org/security.html
- https://sqlite.org/limits.html
- https://sqlite.org/c3ref/limit.html
- https://sqlite.org/c3ref/progress_handler.html
- https://sqlite.org/c3ref/hard_heap_limit64.html
