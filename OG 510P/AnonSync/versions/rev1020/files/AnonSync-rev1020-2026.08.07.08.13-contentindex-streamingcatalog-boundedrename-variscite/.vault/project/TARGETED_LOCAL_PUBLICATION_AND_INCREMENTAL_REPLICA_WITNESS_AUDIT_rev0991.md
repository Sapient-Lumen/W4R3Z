# Targeted local publication and incremental replica witness audit — rev0991

## Product defect

Rev0989 made metadata-only remote effects path-local, but ordinary local file
publication still rebuilt the complete retained replica model twice: once while
preparing an operation and again while committing it. The production folder
loop can observe a 4,096-file segment while the current replica limit retains
10,000 operation envelopes. That shape admitted 8,192 complete model rebuilds
and **81,920,000 prior operation-row decodes** before counting visible-path,
evidence, and causal-projection work. Put differently, one otherwise ordinary
scan segment could approach 100,000,000 prior operation rows merely to publish
new local files.

This was formally bounded but operationally incompatible with the intended
multi-terabyte Linux workflow. A scale fix had to preserve causal identity,
capacity accounting, same-path staleness, schema authority, and crash-atomic
SQLite publication without trusting unrelated mutable generations.

## Retained C++ boundary

Rev0991 raises the replica SQLite schema from v7 to v8 and introduces one
transactionally exact local-publication cutpoint. Preparation now reads only:

- the current typed metadata row;
- the exact visible projection for the target path;
- retained history for that path through the canonical operation-path index;
- the exact active causal frontier required to construct the next operation;
- local actor counter/chain authority and durable policy metadata.

The resulting prepared value carries the exact canonical operation, the
observed target-path heads, a diagnostic state generation, and a sealed
publication cutpoint. The cutpoint intentionally excludes unrelated global
state generation and aggregate operation/evidence/visible digests. Remote
progress on another path may therefore commit concurrently without starving a
local scan. A same-path head or history change makes the prepared publication
stale.

Commit enters one `BEGIN IMMEDIATE` transaction, re-proves the exact schema,
foreign-key mode, and absence of executable TEMP triggers, then re-reads the
same target path, target history, local chain, policy, and causal-head inputs.
It publishes only after the prepared operation and exact cutpoint still agree.
No SQLite writer transaction spans payload or rooted filesystem work.

## Schema-v8 counted commutative witnesses

The previous sorted-stream digests were excellent complete-snapshot witnesses,
but inserting one operation required reconstructing their complete inputs.
Schema v8 adds three fixed-width modulo-2^256 accumulator witnesses:

- active operation identities;
- every retained evidence identity;
- complete visible-path projections.

Each accumulator uses a domain-separated SHA-256 element digest and is bound
separately to an exact cardinality. Visible-path cardinality is stored in the
new `visible_path_count_be` metadata field. A local-operation chain digest
continues to bind the ordered local actor sequence. The new
`sync_replica_operation_paths` table and `(canonical_path, operation_id)` index
make same-path retained history explicit and bounded by the history of that
path.

Complete open, migration, backup, restore, and forensic snapshot paths still
decode and validate every retained operation and recompute both the legacy
canonical-stream digests and the new counted witnesses. The incremental values
are accepted only when they agree with that complete reconstruction. Migrations
from every released schema generation v1 through v7 rebuild the path index and
all schema-v8 witnesses before publication.

These accumulators are **unkeyed structural evidence, not authentication
authority**. Cardinality plus a 256-bit additive witness is not a cryptographic
set commitment and is not presented as one. Authenticated operation envelopes,
canonical decoding, SQLite schema/transaction proof, and complete reconstruction
remain load-bearing.

## Unrelated progress and same-path drift

The publication cutpoint is deliberately path-local. Outbox retries, peer
liveness, clock observations, destination scheduling, and remote operations on
unrelated paths do not determine the canonical local file operation. Allowing
those facts to advance without invalidating prepared work is the liveness gain.

The exact target path is different. A new visible head, a change in retained
same-path history, local actor compromise, local counter/chain drift, policy
change, schema drift, or a different canonical operation invalidates the
prepared authority before effect. Tests prove unrelated history can grow by 192
operations without causing a complete model projection, while pending-path
changes fail closed.

## Rare reverse-dependency fallback

A pathological database can already retain a pending operation that names the
future local operation ID as a predecessor. Inserting the local operation may
therefore activate evidence outside the target path. The normal targeted path
checks the indexed reverse dependency before publication. When one exists, it
falls back to the complete model transition so global activation semantics are
preserved. This is an explicit rare-path correctness fallback, not hidden
normal-path O(history) work.

## Runtime and complexity proof

The focused statement-trace regression creates 192 unrelated retained
operations, prepares and commits one local file, and proves:

- exact target-path history queries;
- bounded active-causal-head queries;
- zero complete operation projections;
- zero complete visible projections;
- no history-dependent query expansion from unrelated rows;
- unrelated remote progress may coexist with commit;
- same-path drift returns a stale cutpoint;
- reverse-dependency activation uses the complete fallback;
- executable TEMP schema is rejected before effects.

The normal retained complexity is **O(history-of-that-path + active causal
heads)** with fixed-width metadata updates. It is not constant memory: active
causal heads and one path's retained history remain bounded vectors. It is also
not a measured multi-terabyte soak, an Android port, content-defined chunking,
rename/move identity, automatic selective-sync eviction, garbage collection, or
ENOSPC qualification.

## Adjacent audit/refactor: idempotence after actor compromise

The first targeted implementation found an existing identical operation ID and
returned `AlreadyPublished` after proving only operation bytes and local-binding
rows. That shortcut was wrong after a same-dot fork had quarantined the retained
operation and marked the local actor compromised: a retry could report success
although the operation no longer carried active local minting authority.

The retained branch now permits `AlreadyPublished` only when the exact retained
operation is still `Active` and the local actor is not compromised. The focused
regression publishes one local file, injects a same-dot fork, proves the actor
and original operation become quarantined, retries the exact prepared value,
and requires a fail-closed exception with no durable state change.

The accumulator arithmetic also gained exact carry and borrow vectors across
the modulo-2^256 boundary. That test guards the fixed-width representation rather
than relying only on ordinary random-looking SHA-256 values.

## Lineage hygiene

The last sealed parent available to this run is rev0989. A previously displayed
rev0990 link was not uploaded into the cloudtainer and cannot be reproduced or
verified. **No rev0990 archive is part of release lineage.** Rev0991 is therefore
constructed directly from exact sealed rev0989 bytes, with the source delta and
reconstruction proof recording that discontinuity rather than inventing an
unavailable parent.

## Validation

Exact rev0991 source passed the GCC 14.2 Debug complete graph across its 470-edge exact-change dependency state, followed by a no-work bundled-SQLite re-attestation, all 270/270 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 1,291 hash-graph, 238 prepared-publication, 361 SQLite-owner, and 536 folder-owner checks. Source audits passed 43/43 SQLite-owner, 30/30 targeted local-publication, and 442/442 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Direct sanitizer proofs passed the same 1,291, 238, 361, and 536 checks; the folder-owner proof peaked at 1,688,812 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0989 parent SHA-256 matched 9af82eab8ce067088e65bf1ca165eb099967b72e18fde3660767454374a9387e and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 596-file projection byte-for-byte and by mode. The final active implementation projection contains 596 files / 27,719,683 bytes with SHA-256 25888965fb9c560846cb528617655c38586f80dd9e27f2c3538baecb83f696b3. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

## Archive

AnonSync-rev0991-2026.08.04.11.50-countedwitness-targetedpublication-quarantinefence-spessartine.zip
