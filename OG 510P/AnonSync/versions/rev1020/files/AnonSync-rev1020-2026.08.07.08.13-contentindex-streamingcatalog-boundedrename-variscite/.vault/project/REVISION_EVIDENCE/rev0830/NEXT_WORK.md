# Next high-leverage work

1. **SQLite VFS fault/crash oracle.** Wrap the production VFS, enumerate returned
   I/O faults and crash images at write/sync/truncate/delete/lock/WAL/shared-memory
   cutpoints, then reopen and join SQLite domain state with receipt publication
   state and typed recovery authority.
2. **Exec-based crash helper.** Move complex SQLite work out of post-`fork()`
   children. Launch a small helper with a typed instruction file or inherited
   descriptor, bounded waits, minimal descriptors/environment, and explicit
   process-exit evidence.
3. **Recovery-authority model corpus.** Express the cross-resource states as a
   small independent model and differentially compare production C++ across
   duplicate, reordered, retry, later-state, identity-race, and crash traces.
4. **Disposable hostile-database worker.** Inspect untrusted SQLite artifacts in
   a one-request process with parent-enforced wall time, CPU/address-space/file
   limits, no-new-privileges, a narrow seccomp policy, and Landlock where
   available. Return a typed value, not a live handle.
5. **Executable convergence algebra.** Classify each durable operation for
   commutativity, idempotence, monotonicity, causality, epoch compatibility, and
   coordination; execute generated reorder/duplicate/partition/restart traces
   against C++.
6. **Privacy and key lifecycle.** Specify authentication, payload
   confidentiality, anonymity, metadata leakage, enrollment, rotation,
   revocation, recovery, forward secrecy, post-compromise recovery, backup, and
   erasure before claiming those properties.
7. **Build-graph decomposition.** Continue extracting invariant-owned slices
   from `src/sync_domain.cpp` (15,257 lines) and
   `include/anonsync_core.hpp` (3,490 lines), with byte-exact behavior contracts
   and one-way no-core dependency guards.
