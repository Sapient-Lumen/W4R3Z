# Rev0798 architecture audit — exact SQLite file geometry

## Boundary

Input is an untrusted, sidecar-free regular-file descriptor plus its exact size.
Output is a narrow `SqliteSnapshotGeometry` capability containing exact bytes,
page size, and page count. No filesystem staging or SQLite open is authorized
until this promotion succeeds.

## Invariants

1. Policy values are nonzero and no greater than reviewed hard ceilings.
2. The 16-byte SQLite signature, including NUL, is exact.
3. Page size is a valid SQLite encoding and power of two.
4. The in-header page count is current, not stale evidence.
5. Page count is nonzero and bounded.
6. Header page extent equals the entire descriptor extent exactly.
7. Geometry is proven before staging allocation.
8. The copied and retained private descriptors reproduce the same geometry.
9. Later seal assertions re-establish geometry before SQLite open/use.
10. Focused tests and fuzzing do not depend on the core monolith.

## Corrected failure mode

SQLite can accept page-aligned suffix bytes outside the header-declared page
graph, while `sqlite3_backup` omits them. Rev0796 authenticated the suffix but
could not truthfully claim the restored database reproduced every authenticated
byte. Rev0798 fails closed before staging.

## Residual risks

- same-size malicious changes by a privileged process or compromised kernel;
- CPU, heap, row, text-byte, and wall-time amplification inside valid geometry;
- interruption during restore publication;
- unknown SQLite implementation defects;
- confidentiality and metadata leakage.

## Recommended continuation

Install an in-process monotone verification budget as defense in depth, then
move hostile snapshot interpretation into a disposable resource-limited worker.
Pair that worker with a VFS crash-cut oracle and an executable protocol outcome
model.
