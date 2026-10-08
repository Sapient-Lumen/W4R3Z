# Local-first stack boundaries — 2026-03-09

This note exists to keep future passes from collapsing a promising product frontier into one fuzzy “sync crate” story.

## Main judgment

The sharper missing Rust crate in this area is not another CRDT engine.
It is a **coordination layer** above several already-meaningful pieces of substrate:

1. **engine lane** — CRDT document/update semantics,
2. **store lane** — durable local persistence and compaction,
3. **transport lane** — ordered replica exchange and reconnect behavior,
4. **membership lane** — device identity, encrypted-group epochs, revocation, and key rotation,
5. **support lane** — redacted bundles, diagnosis reports, and comparability rules.

A good local-first crate should make those lanes inspectable.
It should not quietly imply that convergence, collaboration membership, and supportability are all the same thing.

## What this means for P-0076

Read **P-0076 Local-first Sync Kit** as:

> repo contract → sync state receipts → transport receipts → membership/key-epoch receipts → divergence triage → portable sync bundle

That stack is stronger and more adoptable than either:

- “one more CRDT framework”, or
- “one giant local-first platform that owns everything from storage to identity”.

## Working rule

When touching local-first work in this archive, do **not** collapse:

- CRDT engine choice,
- durable store semantics,
- transport guarantees,
- encrypted-group membership,
- and support artifact design

into one generic claim that “the sync layer handles it”.

Future passes should prefer:

- stable receiver-facing receipts,
- explicit same-user vs shared-group profiles,
- redaction-aware support bundles,
- and conservative divergence classes.

They should avoid:

- pretending E2EE is just a transport checkbox,
- pretending offline convergence implies authorization/revocation correctness,
- or proposing another engine when the sharper gap is the boring coordination artifact above existing engines.
