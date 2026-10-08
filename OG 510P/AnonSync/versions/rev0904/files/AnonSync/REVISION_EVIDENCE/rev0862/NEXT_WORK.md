# Rev0862 next work

1. Inventory every SQLite read and write path by output budget, VM-step budget,
   elapsed budget, busy/lock-wait policy, exact-generation authority, and
   publication boundary. Migrate only after assigning a purpose-specific owner.
2. Separate cooperative SQLite execution deadlines from lock-wait and I/O
   deadlines; do not imply that a progress callback bounds time spent where no
   callback can run.
3. Add planner/access-path attestation for duplicate-heavy frontier queries so
   a reviewed index, query plan, and execution budget reinforce one another.
4. Move hostile database and document interpretation into disposable workers
   with sealed descriptors, bounded request/response protocols, and layered
   process, filesystem, syscall, memory, CPU, and wall-time controls.
5. Continue the product-defining work: an executable operation algebra and
   generated convergence histories, followed by a concrete encrypted
   multi-device identity, key-epoch, revocation, and metadata-leakage model.
6. Reduce the domain monolith and repetitive source-spelling audits by
   extracting typed libraries and replacing lexical invariants with semantic
   reference-model and crash-oracle tests where possible.
