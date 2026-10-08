# Revision notes — rev1019

## Product move

Rev1019 adds conservative identity-preserving regular-file rename/move to the
Linux/headless synchronization path. An exact-content local move now retains
one causal file identity through ordinary File and Tombstone operations, one
immutable payload object, one replica generation, and one catalog generation.
No rename-only wire format or mutable inode identity is introduced.

## C++ implementation

- `SyncReplicaModel` recognizes one canonical destination-File/source-Tombstone
  causal shape after restart.
- `SyncReplicaSqliteOwner` publishes both operations in one `BEGIN IMMEDIATE`
  transaction and one state-generation transition.
- `SyncReplicaFolderScanOwner` discovers a unique absent materialized source,
  re-proves both rooted path authorities, publishes the replica pair, and
  records the exact catalog pair in one catalog transaction.
- Convergence accounting and shipping JSON expose
  `local_identity_preserving_renames`.
- The pass-local source observation is refreshed after publication, avoiding a
  redundant absence observation in the same pass.
- Existing content-addressed payload storage is reused; direct exact-content
  scans reopen the selected digest through targeted access and retain its exact
  inode capability through publication, while convergence passes use their
  retained complete snapshot. The targeted lane is not namespace-health or
  capacity authority. No duplicate payload, payload rename, or new transport
  frame is required.
- The final SQLite pair publication is history-cold: two targeted path histories,
  bounded causal heads, and one streaming current-visible uniqueness scan replace
  a complete retained-state reconstruction.
- A replica-first/catalog-later crash-window regression proves restart adoption
  without another operation or payload.

## Ambiguity correction

The first implementation rejected two absent same-content source candidates but
could still choose one absent source while another same-content File remained
visible. That case would fail late inside publication. Rev1019 moves the
complete current-visible uniqueness fence into planning, before payload or
replica effects. Both still-present and two-absent ambiguity cases now fall back
to ordinary create/delete convergence without inventing identity.

## Adjacent audit/refactor

The folder owner now rejects current-visible content ambiguity before payload
authority, and the SQLite owner independently rechecks it under the final
`BEGIN IMMEDIATE` cutpoint. That final streaming scan now also reconstructs the
complete current-visible projection witness one bounded path at a time. Missing,
reordered, malformed, multiply primary, or otherwise noncanonical rows fail
before either operation can publish; a focused regression proves that deleting
the second same-content row cannot manufacture uniqueness. Restart inference
remains in the model. These are layered cutpoint proofs rather than duplicate
dead helpers.

The adjacent refactor also updates the inherited SQLite source oracle to follow
the generalized plural publication helper and prevents a direct exact-content
scan from rereading the descriptor merely to discover an already retained
payload.

The current release verifier also exposed that the rev1018 wrapper carried
stale rev1017 release metadata and a generated Python bytecode cache. Rev1019
uses the parent archive only as a physical/source lineage input and regenerates
all publication evidence honestly.

## Compatibility and limits

No durable schema, operation codec, reconciliation protocol, delivery protocol,
payload format, selective-sync policy, or control-socket schema changes.

Exact-content copy plus delete is indistinguishable from a rename, so the API
claims causal identity continuity rather than proof of `rename(2)`. The replica
and catalog commits are separately atomic, not one cross-database transaction.
The SQLite pair commit is history-cold, while current folder/model planning
remains O(active evidence or catalog size).
Directory moves, empty directories, portable metadata, conflict UX, retention
collection, ENOSPC recovery, Android adapters, and live public Tor/I2P
qualification remain open.

## Validation

Exact rev1019 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 311/311 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 104 network-model checks plus 41 generated operations, 416 SQLite-owner checks, 562 folder-owner checks, and 114 sync-once checks. The focused identity-preserving-rename source audit passed 31/31 checks and the structural authority audit passed 698/698 checks. An exact Clang 17 ASan/UBSan product graph reached a no-work state against the 284-edge configured product shape, and all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1018 parent SHA-256 matched 02fc26329d2274e6dbf440f3e9d4319a8af08efaa00bdfce8f61c8a59eddf90b; its stale rev1017 release metadata and generated Python cache are explicitly not borrowed as publication authority. The binary-aware source patch reconstructed all 19/19 changed active files. The final active implementation projection contains 649 files / 29,541,244 bytes with SHA-256 ef1df087c17ef62ee25466caeea2e4f105c8716aab3299553b391cc9bcefabf7. Final wrapper-directory verification, ZIP verification and CRC, canonical path/no-symlink policy, and clean-extraction path/byte/type/mode comparison all passed.

## Intended archive

`AnonSync-rev1019-2026.08.07.06.02-causalrename-projectionreproof-singlepayload-bixbite.zip`

Codename: `bixbite`
