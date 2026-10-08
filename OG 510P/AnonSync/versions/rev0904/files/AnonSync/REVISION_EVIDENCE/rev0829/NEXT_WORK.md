# Next high-leverage work

1. **Tri-state durable evidence.** Replace the current Boolean durable-observed
   interpretation with `NotDurable`, `ExactRequestDurable`, and
   `DurableIdentityIndeterminate`. A contradictory result binding must not grant
   automatic replay authority. Add independent reopen/inspection rules for
   promotion from indeterminate to exact.
2. **SQLite VFS fault and crash oracle.** Interpose on database, journal, WAL,
   shared-memory, lock, truncate, delete, write, and sync operations. Enumerate
   I/O errors, process exits, unsynchronized-write reordering, and reopen, then
   join each database state with receipt publication state and a domain oracle.
3. **Exec-based crash helper.** Replace complex post-`fork()` C++/SQLite work in
   test children with a small `exec`-launched helper and a typed instruction
   file or inherited descriptor. This gives deterministic initialization,
   bounded waits, cleaner descriptor ownership, and better failure diagnostics.
4. **Disposable hostile-database worker.** Interpret untrusted SQLite artifacts
   in a one-request process with parent-enforced wall time, CPU/address-space/file
   limits, minimal descriptors and environment, no-new-privileges, seccomp, and
   Landlock where available. Return a small typed result, not a live handle.
5. **Executable convergence algebra.** Classify every durable operation for
   commutativity, idempotence, monotonicity, causal dependence, epoch
   compatibility, and coordination. Differentially execute duplicate, reorder,
   partition, retry, restart, update/delete, and key-epoch traces against C++.
6. **Privacy and key lifecycle.** Separate authentication, confidentiality,
   anonymity, and metadata leakage. Specify enrollment, rotation, revocation,
   recovery, forward secrecy, post-compromise recovery, backup, and erasure
   before naming those as properties.
7. **Build-graph decomposition.** Continue extracting invariant-owned slices from
   `sync_domain.cpp` (15,257 lines) and `include/anonsync_core.hpp` (3,490 lines)
   only with focused byte/behavior contracts and one-way dependency guards.
