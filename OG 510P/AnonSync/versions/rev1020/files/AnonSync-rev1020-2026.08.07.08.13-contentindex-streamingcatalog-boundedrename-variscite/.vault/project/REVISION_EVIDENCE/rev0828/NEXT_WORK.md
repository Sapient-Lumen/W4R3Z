# Next high-leverage work

1. **SQLite VFS fault and crash oracle.** Interpose on every relevant database,
   journal, WAL, and shared-memory I/O operation; enumerate failure/crash cuts,
   unsynchronized-write reordering, truncation, delete, and reopen; then compose
   those traces with receipt temp-write, rename-no-replace, directory sync, and
   recovery classification.
2. **Protocol-level recovery owner.** Replace caller choreography with a small
   typed state machine that owns reset intent, pre-bound receipt capability,
   durable reset evidence, publication effect, residue evidence, and exact replay
   decision. Preserve the no-cross-resource-atomicity claim.
3. **Disposable hostile-database worker.** Interpret untrusted SQLite artifacts
   in a one-request process with parent-enforced time and resource limits, narrow
   descriptors/environment, no-new-privileges, seccomp, and Landlock where
   available; return a small typed result.
4. **Executable convergence algebra.** Classify durable operations for
   commutativity, idempotence, monotonicity, causal dependence, epoch
   compatibility, and coordination; differentially run generated duplicate,
   reorder, partition, retry, restart, update/delete, and epoch-change traces.
5. **Privacy and key lifecycle.** Separate authentication, confidentiality,
   anonymity, and metadata leakage; define enrollment, rotation, revocation,
   recovery, forward secrecy, post-compromise recovery, backup, and erasure
   before claiming those properties.
6. **Build-graph decomposition.** Continue extracting invariant owners from the
   large domain/core translation units only with byte-exact tests, one-way
   dependency guards, and measured before/after build exposure.
