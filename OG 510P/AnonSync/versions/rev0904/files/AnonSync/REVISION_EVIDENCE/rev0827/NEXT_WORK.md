# Next high-leverage work

1. **Combined crash-cut oracle.** Model SQLite VFS state and atomic publication as one
   recovery protocol, including WAL/journal, temporary inode, rename, directory fsync,
   receipt, duplicate retry, and ambiguous syscall outcomes.
2. **Disposable hostile-database worker.** Move untrusted SQLite interpretation into a
   one-request process with parent-enforced time/resource limits and a small typed
   result. Keep seccomp/Landlock/rlimits layered and explicitly report availability.
3. **Executable convergence algebra.** Classify every durable operation for
   commutativity, idempotence, monotonicity, causality, epoch compatibility, and
   coordination requirements; differentially execute generated traces against C++.
4. **Privacy/key lifecycle contract.** Separate authentication, confidentiality,
   anonymity, and metadata leakage. Define device enrollment, epoch rotation,
   revocation, recovery, forward secrecy, post-compromise recovery, backup, and
   erasure before naming those properties as delivered.
5. **Header and translation-unit decomposition.** Continue extracting invariant owners
   from the very large domain/core surfaces only when each extraction has byte-exact
   tests, one-way dependency evidence, and before/after build-graph measurements.
