# Targeted replica path/operation cutpoint and history-scale audit — rev0989

## Product defect

Rev0988 removed the complete-catalog projection from each metadata-only file
removal, but the same effect still reconstructed the complete causal replica
three times: during planning, immediately before rooted unlink, and immediately
afterward. The production pass admits 4,096 remote effects and the replica model
admits 10,000 retained operation envelopes. That composition admitted up to
12,288 complete replica snapshots and model restores in one pass, or as many as
122,880,000 retained operation-row decodes before counting causal-map rebuilds.
It was bounded on paper and still unsuitable for the first supported
multi-terabyte Linux workflow.

## Retained C++ boundary

`SyncReplicaSqliteOwner::targeted_path_cutpoint_or_throw()` now opens one
deferred SQLite read transaction and observes:

- the exact typed replica metadata row;
- at most two `sync_replica_visible` rows selected by canonical path;
- the sole visible operation, when exactly one visible row exists; and
- at most one distinct requested retained operation used to re-prove the folder
  catalog's predecessor mapping.

The visible query is `WHERE canonical_path=? ORDER BY visible_ordinal LIMIT 2`.
Two rows are sufficient to reject sole-visible authority without allocating the
complete conflict set. Operation lookup is by exact primary-key identity. The
canonical operation bytes, operation ID, redundant canonical/context/
predecessor charges, evidence state for a sole visible operation, folder, path,
primary flag, and preservation flag are checked before publication.

When the requested retained identity is also the sole visible identity, the
cutpoint exposes that one owned envelope through a borrowed accessor instead of
creating a second potentially four-megabyte operation-envelope copy. Complete
and targeted readers share `load_stored_operation_row_or_throw()`, so exact and
bulk paths do not maintain divergent operation codecs.

## Composition with rooted dematerialization

A successful metadata-only file removal now uses three targeted replica
cutpoints, matching the three targeted catalog cutpoints introduced in rev0988:
planning, pre-unlink, and post-unlink. No replica writer transaction is retained
across filesystem work. Each cutpoint independently re-proves the current sole
visible target and, when needed, the exact retained catalog predecessor.

The following authority remains unchanged and load-bearing:

- descriptor-rooted source observation and pathname reproof;
- exact catalog and selection-policy cutpoints;
- retained private payload selection and exact inode-use lease;
- causal supersession from the catalog predecessor to the current target;
- atomic rooted displacement, complete displaced-inode hash, and unlink; and
- final rooted absence plus catalog and replica reproof.

Complete replica snapshots remain the authority for pass-level planning,
aggregate operation/evidence/visible/outbox digests, global conflict
projection, retention roots, and terminal settlement.

## Adjacent refactor and audit finding

The first targeted implementation copied stored `state_generation`, policy,
visible-state, and complete cutpoint digests into its result even though the
path-local query did not recompute the global operation, evidence, visible,
outbox, clock, or pin sets. Those fields looked authoritative while carrying
only values read from metadata. They were removed: the targeted result exports
only the operation rows it independently proves.

Each cutpoint does re-attest the exact trigger-free `sqlite_schema` contract and
`PRAGMA foreign_keys` mode in the same deferred read transaction. That cost is
fixed by the compiled schema rather than retained history, and avoids relying
on constructor-time authority after the durable database may have changed.

Canonical operation-row decoding was also centralized. The same decoder now
serves complete snapshots and primary-key reads, including canonical-byte,
identity, charge, and evidence-state attestation.

## Runtime proof

The SQLite-owner regression installs a statement trace and proves:

- one exact visible-path query;
- one operation read when the sole visible target is also the requested
  retained operation;
- two operation reads when the target and retained predecessor differ;
- zero complete operation projections;
- zero complete visible projections;
- one exact schema-catalog attestation and one foreign-key PRAGMA;
- conservative rejection of conflicts, cross-path retained identities, and
  malformed path or operation identities; and
- path-local results remain byte-for-byte identical while unrelated retained
  history advances global state that the targeted result deliberately omits.

A separate folder-owner regression dematerializes eight files and proves 24
exact visible-path reads and 24 exact operation reads while complete replica
operation and visible projections remain pass-bounded. Catalog and causal
evidence remain retained, private payloads remain available, and every selected
rooted name becomes absent.

## Memory and complexity claim

The history-dependent per-cutpoint live projection is bounded by one metadata
row, two small visible rows, and at most two operation envelopes, plus one
fixed-size exact schema observation and foreign-key mode check. The production canonical
operation envelope limit remains 4 MiB. The usual target-equals-catalog-head
case owns one envelope, not two. This removes dependence on total retained
history from the per-file reproof path; it does not make the complete replica
owner constant-memory or qualify target-scale RSS.

## Explicit nonclaims

This targeted cutpoint does not claim to recompute or independently prove the
aggregate operation, evidence, visible, outbox, clock, or retention-pin sets. It
does not prove unrelated paths, replace complete snapshots, create a
cross-SQLite/filesystem transaction, resist a malicious same-UID process, or
provide a formal complexity proof. It is not a measured multi-terabyte soak,
content-defined chunking, placeholders, automatic private-payload eviction,
garbage collection, Android support, or ENOSPC qualification.

The next product edge is measurement and pressure reduction on the first real
Linux media-tree workload, followed by insertion-resilient delta and
identity-preserving rename/move. The source audit is lexical hygiene, not
semantic proof; compiler, runtime, sanitizer, scale, reconstruction, and package
evidence remain load-bearing.

## Validation and archive

Exact rev0989 source passed the GCC 14.2 Debug complete graph in its 540-edge configured dependency state, followed by a no-work bundled-SQLite re-attestation, all 269/269 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 356 SQLite-owner checks and 536 folder-owner checks. Source audits passed 52/52 selective-sync checks, 24/24 targeted catalog-cutpoint checks, 30/30 targeted replica path-cutpoint checks, and 433/433 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed with leak detection and halt-on-error, including direct 356-check SQLite-owner and 536-check folder-owner proofs. The sanitized folder-owner proof peaked at 1,664,276 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0988 parent SHA-256 matched 067de76a76061db941ebccde03821c84134428152784954a51feba153505d23d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 593-file projection byte-for-byte and by mode. The final active implementation projection contains 593 files / 27,588,416 bytes with SHA-256 195b1897e39b44b6f32d2838ee6eff35dc65849de7a3e2e70c6bb0882d43ea4a. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

`AnonSync-rev0989-2026.08.04.07.53-targetedreplica-historybounded-pathreproof-larimar.zip`
