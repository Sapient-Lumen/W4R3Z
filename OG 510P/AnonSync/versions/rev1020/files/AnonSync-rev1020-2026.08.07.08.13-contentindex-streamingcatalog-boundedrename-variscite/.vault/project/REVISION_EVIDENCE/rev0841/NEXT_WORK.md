# AnonSync rev0841 next work

## P0 — make convergence executable

Create a small dependency-light C++ reference model for durable operations. Define for
each operation whether it is commutative or order-sensitive, idempotent or single-use,
monotone or retracting, causally dependent or independent, and coordination-free or
coordinated. Generate duplicate, reordered, partitioned, concurrent update/delete,
retry, restart, schema-epoch, and key-epoch traces. Differentially compare the production
engine with the reference state and minimized counterexample histories.

Do this before adding more transport features. A valid local history is not sufficient if
replicas with the same authorized operations can disagree.

## P0 — finish machine-byte ownership

Classify every remaining production stream. Prioritize:

1. `replay_ledger.cpp` JSONL entries and journal documents;
2. `reporting.cpp` machine reports;
3. `sync_operator_cli.cpp` status/JSON output;
4. remaining signing and JSON construction in `runner.cpp`; and
5. snapshot-manifest v2 compatibility construction.

For machine bytes require a frozen owner, deterministic versioned encoding, locale-free
numbers, well-formed UTF-8 or explicit opaque bytes, field and document budgets, and a
global-locale perturbation test. Do not claim RFC 8785 unless the complete scheme is
implemented and interoperably tested.

## P0 — build a cross-resource crash oracle

Model each durable transition across SQLite main/WAL state, staging files, atomic rename,
parent-directory sync, manifests, receipts, checkpoints, and downstream effects. Inject
cuts before and after every observable step. Recovery must produce one of a finite set of
allowed states and must never claim an external effect that lacks the bound ledger/receipt
state or silently replay a single-use effect.

## P1 — isolate hostile interpretation

Add a disposable Linux worker boundary that accepts only pre-opened descriptors and a
small request record. Apply `no_new_privs`, resource limits, a minimal seccomp filter,
Landlock rules where supported, closed inherited descriptors, an empty environment,
wall-clock supervision, and bounded response framing. Treat seccomp as one attack-surface
reduction layer, not as the complete sandbox.

Start with sealed SQLite snapshot verification because it already has byte and execution
budgets and a narrow result shape.

## P1 — define the privacy and device/key protocol

Write an explicit threat model and wire/state model for:

- payload encryption and content addressing;
- membership and device enrollment;
- device/service generations and key epochs;
- rotation, revocation, lost-device recovery, and state-loss recovery;
- forward secrecy and post-compromise recovery;
- metadata leakage, traffic analysis, padding, and delivery-service observability;
- backup key custody and rollback protection; and
- deletion/erasure limits on real storage.

Authentication of heartbeat or transition evidence must remain separate from these
properties. Consider established group-key protocols, but integrate them only after
specifying how synchronization state, identities, delivery, and metadata are handled.

## P1 — reduce change amplifiers

Extract the 15,287-line domain translation unit into invariant-owned libraries with one-way
CMake dependencies. Split the 9,348-line selftest owner into production-facing focused
tests. Generate repetitive CMake test/target declarations from small checked data where
possible, while keeping the generated result reviewable.

Track preprocessed lines, object build time, peak RSS, and dependency edges for every
extraction. A file split with no ownership improvement is not progress.

## P2 — make evidence economical

Stop recursively carrying the full historical evidence corpus in every normal handoff.
Create periodic checkpoint archives and a content-addressed evidence index keyed by
SHA-256. Keep the current revision's source diff, active projection, validation summary,
defect witnesses, and exact parent hash in the package. Preserve old evidence externally
or in occasional archival checkpoints.

Review every lexical audit for retirement after a typed boundary, compile-time dependency
rule, semantic test, or model oracle supersedes it.
