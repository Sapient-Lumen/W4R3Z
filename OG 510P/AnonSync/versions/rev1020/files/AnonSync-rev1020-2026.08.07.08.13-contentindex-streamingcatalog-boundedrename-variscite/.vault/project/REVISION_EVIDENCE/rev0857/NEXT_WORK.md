# Next work after rev0857

1. **Give each logical object an explicit incarnation.** Path plus content and
   lineage cannot safely distinguish deletion followed by recreation. Bind
   object generation and creation authority before extending conflict policy.

2. **Define causal operation identity.** Specify update, delete, recreate,
   rename, directory move, conflict preservation, and external effects in one
   deterministic reference model. Exercise duplicate, reordered, partitioned,
   restarted, and multi-peer histories against C++.

3. **Bound manifest interpretation, not only hashing.** Add explicit entry,
   chunk, lineage, path-byte, and total-byte budgets at the earliest parser and
   validation boundary. Prove exhaustion behavior before allocation growth.

4. **Move hostile interpretation out of the principal process.** Decode and
   validate peer manifests, documents, and SQLite snapshot evidence in a
   disposable worker with sealed descriptors, CPU/memory/output limits,
   filesystem isolation, and a narrow request/result protocol.

5. **Join identity to cross-resource crash semantics.** Inject cutpoints across
   checkpoint transactions, staged-file publication, directory barriers,
   preserved conflicts, receipts, and externally visible effects. Recovery
   must re-establish one authorized state, not merely re-hash it.

6. **Specify the privacy and key plane.** Define payload encryption, device and
   membership generations, key epochs, rotation and revocation, lost-device
   recovery, forward secrecy, post-compromise recovery, metadata leakage,
   rollback resistance, and backup custody before relying on “Anon.”

7. **Reduce proof cost.** Extract more invariant-owned leaves from
   `sync_domain.cpp`, generate repetitive CMake inventories from checked data,
   replace lexical audits with semantic or compile-time boundaries, and stop
   carrying unnecessary historical evidence through routine engineering
   handoffs.
