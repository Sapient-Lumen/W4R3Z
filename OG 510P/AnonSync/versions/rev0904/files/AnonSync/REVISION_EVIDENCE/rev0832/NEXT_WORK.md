# Next work after rev0832

1. Migrate isolation-only raw forks in peer-ingress schema attestation, runtime payload-store crash testing, and atomic-publication tests to `SelfExecTestProcess`; retain separate inheritance micro-oracles only where required.
2. Extract remaining large diagnostic ownership from `src/reporting_selftests.cpp` and continue shrinking production compile surfaces without changing diagnostic semantics.
3. Build the executable convergence algebra: classify durable transitions by commutativity, idempotence, monotonicity, causal dependencies, epoch compatibility, and coordination requirement, then differentially execute generated traces against production C++.
4. Add a disposable hostile-SQLite worker with parent-enforced CPU, wall-clock, address-space, file-size, descriptor, and syscall/filesystem limits.
5. Expand crash testing from application-selected cutpoints toward a VFS/publication oracle that evaluates SQLite, receipts, manifests, sidecars, and directory durability as one recovery protocol.
