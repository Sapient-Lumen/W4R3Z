# Rev0855 next work

## Highest-value product work

Define a small executable convergence model before adding more persistence
boundaries. Specify object identity, operation identity, causal context,
recreation epochs, delete semantics, rename semantics, schema/key epochs, and
externally visible effects. Generate duplicate, reordered, concurrent,
partitioned, retried, and restarted histories and compare the C++ result with a
small deterministic reference model.

## Highest-value C++ safety work

Continue eliminating borrowed raw `sqlite3*` compatibility overloads at
invariant-owned module boundaries. The next useful extraction is a typed
busy-timeout configuration operation that consumes an exact-generation borrow,
leaving the raw overload only at the narrowest legacy adapter.

Audit close ordering for every object that may retain a SQLite mutex entry or
client-data sentinel. The new scoped owners enforce their own affinity, but
foreign concurrent close remains outside their proof boundary.

## Highest-value isolation work

Move hostile SQLite/document interpretation into disposable workers with sealed
descriptors, bounded requests, CPU/memory/output/descriptor limits, and layered
syscall/filesystem restrictions. Treat the worker result as an untrusted frozen
value that must be revalidated by the principal process.

## Waste reduction

Replace repetitive CMake target and audit registration blocks with checked data
from which CMake and inventory tests are generated. Retire lexical audits when a
typed API or semantic oracle fully supersedes them. Keep historical evidence
available, but stop recursively copying old validation logs into routine build
inputs or search scopes.
