# AnonSync rev0796 — sealed snapshot bytes, WAL exclusion, and VFS identity

Prepared from the independently verified byte parent
`AnonSync-rev0792-2026.07.15.04.14-schematruth-norepair-ddlfence-enforcementproof.zip`. Parent SHA-256 and all 25 package-verifier checks are
recorded under `REVISION_EVIDENCE/rev0796/lineage/`.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Observation is not
authority. Durable state may be promoted only after the boundary that owns an
invariant verifies the exact bytes, identity, process, generation, schema,
relationship, policy, and durability evidence required for that transition.

For snapshots, the bytes authenticated by a manifest must be the same bytes
SQLite interprets, prefix checks inspect, and restore copies. A pathname is not
such a capability.

## Severe defect corrected: an unsigned WAL could alter signed state

Rev0792 hashed only the main snapshot file and later opened its pathname through
SQLite. SQLite could merge a regular sibling `-wal` into the logical database.
The WAL was outside `snapshot_sha256` but inside read-only verification and
`sqlite3_backup`.

The preserved reproducer changes a valid outbox row only in WAL while the main
SHA-256 remains unchanged. Rev0792 accepted and restored the unsigned `inflight`
state; rev0796 rejects before opening SQLite and publishes no destination.

## Refactor: one sealed-snapshot owner

`src/persistence/sqlite_snapshot_seal.*` is a move-only process-local capability.
Capture now traverses and retains a symlink-free parent identity, rejects WAL/SHM/
journal sidecars, opens one single-linked regular source through retained-parent
`openat` and `O_NOFOLLOW`, enforces a one-GiB ceiling, copies and SHA-256 hashes
the exact stream into a private 0700 directory, makes the staged file 0400,
re-hashes that staged descriptor before promotion, retains inode evidence, pins
the selected SQLite VFS by name and pointer, and opens only the staged inode via
`mode=ro&immutable=1&cache=private`.

Manifest digest comparison, logical verification, prefix continuity, and
restore backup all consume the same seal. The original hostile pathname is not
reopened after capture.

The path-family boundary was extracted from the monolithic core into its own
library. The stale persistence inventory was also repaired: it now scans active
code only, strips comments/literals, distinguishes tests from production, and
fail-closes if raw scalar extraction escapes `sqlite_exact_value.cpp`.

## Untrusted SQLite profile

Before traversing hostile schema or rows, the verifier confirms defensive mode,
untrusted schema, disabled triggers/views/extensions/DQS, disabled ATTACH
creation and writes where available, bounded SQLite limits, query-only mode,
foreign keys, cell-size checking, and zero memory-mapped I/O.

## Verification

- Parent package verification: **25/25**.
- GCC 14 Debug/`-Werror`: full build and **56/56 CTest**.
- Focused seal proof: **56 checks × 20/20**.
- Integrated WAL-binding proof: **10 checks × 20/20**.
- Existing read-only verifier proof: **9 checks × 20/20**.
- Clang 17 strict conversion/sign-conversion `-Werror`: **5/5**.
- GCC 14 first-party `-O3 -DNDEBUG` strict lane: **5/5**.
- GCC 14 first-party ASan/UBSan lane: **5/5**.
- Twelve deterministic authority/architecture audits: all passed; seal audit **37/37**.

The focused proof is 8 Ninja actions and 3 first-party translation units
(1,679 lines). The integrated proof and core expose 52 actions and the
22-TU, 49,119-line core archive.

## What remains missing

The one-GiB ceiling does not yet bound page count, row count, VDBE steps, SQLite
heap, allocation volume, or wall time. The next resource revision should install
a versioned progress-handler budget and explicit page/row ceilings.

Private staging temporarily duplicates plaintext bytes. A reviewed descriptor-
backed VFS or content-addressed immutable object could remove that amplification,
but would enlarge the trusted computing base and requires fault-injection proof.

The larger priorities remain a crash-cut VFS/protocol oracle, replay-evidence
provenance and pruning commitments, a formal convergence model, and an explicit
privacy/adversary contract. Authentication and sealed persistence still do not
by themselves establish anonymity or content confidentiality.

## Explicit proof boundary

Rev0796 proves that one sidecar-free byte stream is captured, digested twice,
decoded, and restored through one process-local capability under the tested
POSIX and bundled-SQLite profile. It does not prove protection against a
privileged process or kernel, confidentiality of snapshot contents, bounded
total verifier work, or crash consistency across every filesystem publication
cut.
