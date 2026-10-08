# Next work after rev0856

1. **Give objects explicit recreation identity.** Path plus content digest cannot distinguish delete/recreate epochs safely. Add object incarnation and causal context before expanding the conflict policy.

2. **Model rename as an operation, not delete plus create by accident.** Define concurrent rename/modify/delete semantics, cycles, case-folding collisions, and directory moves, then extend the generated-history oracle.

3. **Build the complete convergence reference model.** Feed duplicate, reordered, partitioned, restarted, and multi-peer histories into a small deterministic model and compare materialized primary state, tombstones, preserved artifacts, and authority receipts with C++.

4. **Join convergence to crash recovery.** Inject cutpoints across manifest/checkpoint updates, preserved-file publication, directory barriers, SQLite transactions, and downstream effects. A semantic winner is insufficient if crash recovery can publish half a transition.

5. **Separate hostile interpretation.** Move hostile manifests, SQLite snapshots, and document decoding into disposable resource-bounded workers with a sealed request/result protocol.

6. **Specify the privacy plane.** Define payload encryption, device and membership generations, key epochs, rotation/revocation, lost-device recovery, forward secrecy, post-compromise recovery, metadata leakage, rollback resistance, and backup custody before relying on the “Anon” name.

7. **Reduce proof cost.** Continue extracting invariant-owned leaves from `sync_domain.cpp`, replace source-spelling audits with semantic tests where possible, generate repetitive CMake declarations from checked data, and stop copying unnecessary historical evidence into routine engineering handoffs.
