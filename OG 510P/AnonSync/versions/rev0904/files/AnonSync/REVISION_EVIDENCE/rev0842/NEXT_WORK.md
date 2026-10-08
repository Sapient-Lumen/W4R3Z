# AnonSync rev0842 next work

## P0 — build one cross-resource crash oracle

Model the local commit protocol as explicit states and observable resources rather than
as independent helper tests. At minimum include:

- ledger main file, temporary file, and parent directory entry;
- recovery journal creation, file fsync, directory fsync, and removal;
- SQLite main/WAL/SHM families where applicable;
- snapshot manifests, restore staging, receipts, and checkpoint ownership;
- downstream effect observation and terminal transition evidence.

Inject process termination and I/O failure before and after every externally observable
step. Recovery must end in a finite allowlist of states. It must never report a durable
transition whose bound bytes are absent, silently replay a single-use effect, accept a
journal describing different bytes, or discard the only witness needed to choose the
correct recovery branch.

The first concrete correction to examine is journal-entry durability: a newly created and
fsynced journal file does not by itself prove that the containing directory entry is
persistent. Decide and test the required directory-fsync point before ledger namespace
publication begins.

## P0 — introduce a directory-descriptor namespace owner

Create a Linux implementation based on trusted directory descriptors and `openat2` where
available. Consider these resolution constraints deliberately:

- `RESOLVE_BENEATH` or `RESOLVE_IN_ROOT` for confinement;
- `RESOLVE_NO_SYMLINKS` and `RESOLVE_NO_MAGICLINKS`;
- optionally `RESOLVE_NO_XDEV` where crossing mount points is outside policy.

Open, inspect, read, replace, rename, fsync, and unlink relative to the same directory
owner. Preserve a portable fallback with narrower documented guarantees rather than
pretending `O_NOFOLLOW` on the final component protects the whole path.

Add adversarial tests for parent-component replacement, bind mounts where available,
magic links, rename races, hard-link aliases, deleted-but-open objects, and directory
replacement between observation and publication.

## P0 — make convergence executable

Define a small deterministic reference model before adding more transport or storage
features. Its operation vocabulary should cover:

- create/update/delete/recreate and rename;
- immutable object generation and folder/device identity;
- causal predecessor sets or clocks;
- duplicate, reordered, and delayed delivery;
- concurrent content and metadata edits;
- schema, policy, membership, and key epochs;
- tombstone retention and garbage-collection preconditions; and
- operations that require coordination rather than a merge rule.

Generate histories with partitions, retries, crashes, and restarts. Compare every
production transition and final replica state with the model. A valid hash chain is an
input to this proof, not the proof itself.

## P1 — split replay-ledger orchestration by authority

`src/replay_ledger.cpp` now has a better publication owner but grew to 1,142 lines. Split
it into one-way dependencies:

1. frozen row/journal value and codec;
2. exact decoder and ledger semantic validator;
3. namespace and descriptor owner;
4. durable replacement protocol;
5. backend orchestration and public API.

Measure preprocessed lines, object build time, peak compiler RSS, and dependency edges.
Reject file splits that preserve the same broad include and state reachability.

Apply the same approach to `src/sqlite_replay_ledger.cpp`: move snapshot-manifest trust
verification and effect-transition record integration behind narrow production-facing
interfaces. Do not add another lexical audit as a substitute for a dependency boundary.

## P1 — mint framed successors for legacy material

Retain read compatibility, but define framed vNext formats for:

- local replay entry hash material;
- local replay recovery journals;
- SQLite snapshot manifests; and
- durable effect-transition records.

Use named, length-prefixed fields, explicit version/context markers, locale-free integers,
fixed text policy, and aggregate limits. Include migration tests that read historical
records, append only the new format, and prove mixed-history replay.

## P1 — isolate hostile interpretation

Move hostile SQLite/document interpretation into a disposable worker with a bounded
request/response protocol and pre-opened descriptors. Apply CPU, memory, descriptor,
wall-clock, filesystem, network, and syscall restrictions. Treat seccomp as attack-surface
reduction, not a complete sandbox. Kill the worker on malformed framing, excess output,
timeout, or unexpected descriptor use.

Snapshot verification is a good first candidate because its input, budget, and result
shape are already narrow.

## P1 — define the privacy and device/key protocol

Before presenting anonymity or confidentiality as product properties, specify:

- payload encryption and content addressing;
- membership, device enrollment, and device generations;
- key epochs, rotation, revocation, and lost-device recovery;
- state-loss recovery and rollback protection;
- forward secrecy and post-compromise recovery;
- metadata leakage, traffic analysis, padding, and delivery observability;
- backup key custody; and
- realistic deletion/erasure limits.

Keep authentication of local evidence separate from these properties.

## P2 — make validation and evidence cheaper

Replace line-count and source-spelling audits with typed/dependency/semantic enforcement
where possible. Generate repetitive CMake test declarations from a checked data table if
that reduces copy-paste without hiding the final target graph.

Move old revision evidence into content-addressed periodic checkpoint archives. Ordinary
handoffs should carry the current active projection, source patch, validation summary,
lineage, defect witnesses, and a compact index rather than recursively duplicating all
historical evidence.
