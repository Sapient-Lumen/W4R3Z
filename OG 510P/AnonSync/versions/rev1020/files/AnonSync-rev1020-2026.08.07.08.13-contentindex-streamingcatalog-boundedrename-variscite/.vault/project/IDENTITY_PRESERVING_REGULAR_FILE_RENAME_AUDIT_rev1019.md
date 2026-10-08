# Identity-preserving regular-file rename audit — rev1019

## Product purpose

The first supported workflow is Linux/headless synchronization of large media
trees. Delta transfer and selective synchronization are mandatory, but ordinary
file semantics also matter: renaming a large retained file must not become a
new unrelated identity that duplicates payload storage, destroys causal
history, or forces peers that already retain the exact payload to fetch it
again.

Rev1019 closes the first regular-file rename/move slice without introducing a
rename-only wire operation. The durable history remains ordinary immutable File
and Tombstone operations. The implementation recognizes one conservative
causal shape as an identity continuation and otherwise falls back to the
existing create/delete behavior.

## Canonical causal shape

A local exact-content rename publishes two operations under one actor epoch:

1. a destination File whose observed causal context includes the exact source
   File; then
2. a source Tombstone at the immediately following actor counter whose sole
   predecessor is that destination File.

The model recognizes the identity continuation only when the destination's
observed namespace contained exactly one visible File anywhere with the same
size and SHA-256 digest, that File was the sole visible value at the source
path, both operations remain active, and every actor/counter/context relation
is exact. Unknown, inactive, malformed, conflicted, content-changing, or
ambiguous evidence yields no identity continuation.

An exact-content copy followed by deletion is observationally indistinguishable
from a filesystem rename at this layer. The result is therefore **causal
identity continuity**, not proof that `rename(2)` or any particular filesystem
operation occurred.

## Local publication authority

The SQLite replica owner publishes the destination File and source Tombstone in
one `BEGIN IMMEDIATE` transaction. Both capacity checks occur before commit,
the two consecutive operation IDs are durable together, and the replica state
generation advances once. A failure while admitting the second operation
cannot expose a destination-only half rename. This path is history-cold: it
reads only the two targeted path histories, bounded active causal heads, and one
streaming current-visible uniqueness scan; it does not call the complete
retained-state loader.

The folder owner plans identity continuation only for a materialized cataloged
source File whose rooted path is currently absent and whose exact content is
unique across the current active visible namespace. It then:

- re-proves selective-sync authority for both source and destination;
- re-proves destination bytes through the ordinary prepared-file boundary;
- proves the source remains absent through descriptor-rooted observation;
- synchronizes and re-proves both rooted parent authorities before database
  publication;
- records source Tombstone and destination File in one folder-catalog
  transaction and one catalog generation; and
- refreshes the pass-local source observation so the same convergence pass does
  not spend a redundant authoritative absence observation.

The private immutable payload object is reused. A direct exact-content single-path scan first reopens the selected
operation through the bounded targeted-access lane; this covers both the rename
and the later no-op path. The targeted owner and exact-inode lease remain live
through replica and catalog publication, and ordinary descriptor admission is
used only if that exact payload is genuinely missing. Targeted access does not
become complete payload-namespace health or capacity authority; the convergence
pass keeps that role through its already-paid complete snapshot. No payload
rename, quarantine, unlink, or duplicate payload publication occurs. A
peer that already retains the exact source digest can satisfy the destination
through existing content-addressed and delta-reuse paths; rev1019 does not add a
new transport message.

## Ambiguity and fallback

Two independent ambiguity fences are required:

- if two absent cataloged source names have the same size and digest, neither is
  selected as the rename source;
- if another still-visible File anywhere has the same size and digest, rename
  planning stops before payload or replica publication.

Both cases use ordinary create/delete convergence. This may lose rename
identity, but it never invents identity from duplicate content.

## Crash and restart boundary

The replica pair is atomic inside the replica database, and the catalog pair is
atomic inside the catalog database. Those databases remain separate authority
owners; rev1019 does **not** claim one cross-database transaction. A process can
crash after the replica pair commits and before the catalog pair commits. The
focused regression deliberately creates that cutpoint, destroys the scanner,
and requires restart to adopt the existing destination File and source
Tombstone without publishing another replica operation or payload. Ordinary
causal projection, rooted observation, catalog adoption, and absence repair
converge from durable evidence rather than trusting an in-memory rename flag.

The identity itself is inferred from retained operations after restart. No
mutable inode number, watcher cookie, process-local pointer, or transport-only
rename bit becomes durable authority.

## Complexity and limits

This is a bounded product-semantic correction, not a million-file rename
throughput proof. The final SQLite publication is path-targeted and history-cold,
but current folder planning still reconstructs the retained model and scans
active visible evidence plus catalog state. Diagnostic restart inference also
remains O(active evidence). No whole-payload-byte copy is introduced when the
source digest remains retained, but namespace scale, model reconstruction, and
SQLite cost still need real dense-tree measurement.

Rev1019 covers regular files only. It does not add first-class directory or
empty-directory operations, directory subtree moves, portable metadata
preservation, hard links, symlinks, case-only rename policy, Unicode
normalization policy, conflict-copy UX, Android storage adapters, retention
collection, quota/ENOSPC recovery, or live public Tor/I2P qualification.

## Adjacent audit and release hygiene

The audit replaced avoidable direct-scan payload re-admission with exact
targeted reuse, retained that capability through both publication cutpoints,
and updated the inherited SQLite source oracle to follow the generalized plural
publication helper. It also found that the final uniqueness query could infer
"one matching File" from a damaged `sync_replica_visible` projection if a
same-content row vanished while the durable projection witness remained
unchanged. The already-required streaming current-visible scan now reconstructs
one bounded path view at a time, validates ordinals, primary and preservation
flags, recomputes the complete visible-path count and accumulator digest, and
compares both with durable metadata before either operation can publish. A
focused corruption regression removes the duplicate row, requires fail-closed
rejection, restores it, and proves that no operation escaped.

The audit keeps two deliberately different ambiguity fences. The folder owner
rejects obvious ambiguity before payload authority, while the SQLite owner
rechecks complete current-visible content and its retained projection witness
under the final `BEGIN IMMEDIATE` cutpoint. The model remains the restart
inference oracle.

The sealed rev1018 archive was also rechecked with the current wrapper-aware
verifier. Its physical SHA-256 can be used as lineage, but its staged release
metadata was not self-consistent: stale rev1017 gate/manifest/evidence and a
Python bytecode cache caused the current verifier to pass only 30 of 41 checks.
Rev1019 therefore borrows no publication claim from that gate. It reconstructs
from the Git-recorded rev1018 source baseline, removes generated cache files,
and regenerates projection, evidence, release gate, manifest, and archive
verification from the final rev1019 tree.

## Validation scope

Exact rev1019 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 311/311 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 104 network-model checks plus 41 generated operations, 416 SQLite-owner checks, 562 folder-owner checks, and 114 sync-once checks. The focused identity-preserving-rename source audit passed 31/31 checks and the structural authority audit passed 698/698 checks. An exact Clang 17 ASan/UBSan product graph reached a no-work state against the 284-edge configured product shape, and all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1018 parent SHA-256 matched 02fc26329d2274e6dbf440f3e9d4319a8af08efaa00bdfce8f61c8a59eddf90b; its stale rev1017 release metadata and generated Python cache are explicitly not borrowed as publication authority. The binary-aware source patch reconstructed all 19/19 changed active files. The final active implementation projection contains 649 files / 29,541,244 bytes with SHA-256 ef1df087c17ef62ee25466caeea2e4f105c8716aab3299553b391cc9bcefabf7. Final wrapper-directory verification, ZIP verification and CRC, canonical path/no-symlink policy, and clean-extraction path/byte/type/mode comparison all passed.

Intended archive: `AnonSync-rev1019-2026.08.07.06.02-causalrename-projectionreproof-singlepayload-bixbite.zip`

Codename: `bixbite`
