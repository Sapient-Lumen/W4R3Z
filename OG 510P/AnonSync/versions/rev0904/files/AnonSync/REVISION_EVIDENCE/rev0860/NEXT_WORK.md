# Next work after rev0860

1. Inventory every specialized manifest, workorder, receipt, and sidecar row
   loop. Classify each as complete reconstruction, bounded subset proof,
   existence proof, uniqueness proof, or aggregate proof, then give it a typed
   row/byte/step budget.
2. Bind query authority to schema and index identity, not merely SQL spelling.
   Measure and cap SQLite VM steps so an attested but pathologically planned
   query cannot consume unbounded CPU.
3. Move hostile SQLite and document interpretation behind a disposable worker
   protocol with descriptor-only inputs, bounded outputs, CPU/memory/time
   limits, filesystem confinement, and fail-closed parent verification.
4. Continue extracting invariant owners from `sync_domain.cpp`; integrations
   should orchestrate typed capabilities rather than contain persistence loops.
5. Return to the product-defining gap: an executable operation algebra and
   generated multi-peer histories for update, delete, recreation, rename,
   membership/key epochs, partitions, retries, restart, and external effects.
6. Specify the privacy plane: payload encryption, device generations,
   membership, rotation, revocation, recovery, forward secrecy,
   post-compromise recovery, and metadata leakage.
