# Next work after rev0833

1. Extend `SelfExecTestProcess` with bounded nonblocking stdout/stderr capture, then migrate `sqlite_transaction_allocator_fault_test.cpp` away from its manual fork/dup2/exec bridge.
2. Give every remaining raw inheritance/lineage probe a common monotonic timeout, kill, and exact reap owner; split child-local success scenarios into fresh-image helpers.
3. Continue extracting diagnostic ownership from `src/reporting_selftests.cpp` and shrinking high-cost production compile surfaces without changing test semantics.
4. Build the executable convergence algebra: classify durable transitions by commutativity, idempotence, monotonicity, causal dependency, epoch compatibility, and coordination requirement, then differentially execute generated traces against production C++.
5. Add a disposable hostile-SQLite worker with parent-enforced CPU, wall-clock, address-space, file-size, descriptor, syscall, and filesystem limits.
6. Expand application-selected crash frontiers toward a VFS/publication oracle that evaluates SQLite, receipts, manifests, sidecars, temp artifacts, and directory durability as one recovery protocol.
