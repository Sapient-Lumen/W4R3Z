# Heartbeat document boundary inventory

- Typed header: 66 lines
- Implementation: 647 lines
- Focused adversarial corpus: 428 lines, **39/39** checks
- Structural audit: 287 lines, **26/26** checks
- Dedicated library: `anonsync_sync_daemon_heartbeat_document`
- Leaf archive inputs: one C++ object
- Focused test link graph: the leaf archive only; no `anonsync_core_lib` backedge
- Runtime direction: `anonsync_core_lib` privately consumes the leaf
- Unresolved first-party symbols in the leaf archive: zero

The leaf owns canonical JSON meaning, exact-number limits, stale-horizon arithmetic, owner geometry, release/finality coherence, lockless residue rejection, and validating serialization. The domain still owns checkpoint/session path policy, durable-row comparison, service-instance derivation, and takeover decisions.

Known compile-time cost: the implementation still includes the large internal type umbrella to obtain the options/result snapshots used by serialization. Splitting a narrow immutable serialization view is a future refactor.
