# Plan 9 lesson: Venti/Fossil-style *write-once* content-addressed archival storage

DeriveBSD already wants content-addressed artifacts and immutable receipts.
Plan 9’s **Venti** and **Fossil** show a clean way to turn that into an *operational superpower*:

- **Venti**: a content-addressed block store where the *hash is the address* (and blocks are write-once)
- **Fossil**: an archival file server built on top of Venti, with cheap snapshots and long retention

The lesson is not “run Plan 9.”
The lesson is: **make your forensics / rollback / support history structurally hard to destroy**.

## What to steal

1) **Write-once by construction**
If the key *is* the hash, you don’t overwrite; you only add.
Accidental corruption becomes detectable, and “delete history” becomes a *separate* capability (if it exists at all).

2) **Dedupe is not an optimization — it’s the model**
Repeated receipts, logs, snapshots, and bundles collapse onto shared blocks.

3) **Snapshot trees are just more hashes**
You can represent “system state at time T” as a tree of digests, where the roots are named by a revocable directory.

## DeriveBSD adaptation

### 1) Evidence Vault: a WORM-ish store for receipts and incident artifacts
Introduce an optional **evidence vault** service:
- stores evidence objects (apply receipts, audit chunks, trace slices, support bundles)
- keyed by digest (CAS)
- append-only by default
- retention and deletion are explicit, policy-governed operations with receipts

This complements the main store (`docs/03-store.md`) without conflating “build artifacts” and “operational evidence”.

### 2) Name indirection for revocation + retention
Use the Amoeba-style “name → capability set” directory idea (`docs/345-amoeba-bullet-server-and-capability-directories.md`):
- human names point to *current* roots (digests)
- rotating a name to a new root is cheap
- revoking a name does not require rewriting blocks

### 3) Integration points
- Evidence spine (`docs/229-evidence-spine-overview.md`): receipts can be stored/replicated as immutable blobs.
- Incident snapshots (`docs/216-incident-snapshots-and-support-bundles.md`): support bundles become *addressed objects* with stable digests.
- Flight recorder tracing (`docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`): trace slices can be sealed and stored as bounded evidence.
- ZFS (`docs/27-vm-storage-zfs.md`): ZFS snapshots are great locally; the vault is about **durable, portable, deduped history**.

## Practical design sketch (minimal version)

- Block size (e.g., 4–64KiB) chosen for store ergonomics.
- Blocks addressed by a digest (hash-agile: see ADR-0013).
- Trees (Merkle-ish) represent larger objects; roots are digests.
- A small “directory” service maps names to roots (policy-gated updates).
- GC is **lease-driven** (nothing is collected unless policy says it may be).

## Why bake this in now?

Because otherwise:
- evidence becomes “log files somewhere”
- retention is ad-hoc and fragile
- “support bundles” drift into manual one-offs
- rollback history is easy to lose when you need it most

Greenfield advantage: treat immutable evidence as a *first-class artifact lane*.

## References
- Venti paper (Quinlan/Dorward): https://9p.io/sys/doc/venti/venti.pdf
- FAST’02 paper page (context + citation entry): https://www.usenix.org/conference/fast-02/venti-new-approach-archival-data-storage
- Fossil paper (Quinlan/McKie/Cox): https://p9f.org/sys/doc/fossil.pdf
- Plan 9 papers index (handy jump table): https://9p.io/wiki/plan9/papers/
