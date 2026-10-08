# Manifest reference and delta index cache audit — rev0992

## Product defect

Rev0986 made large-file transfer bounded and capable of exact fixed-block
predecessor reuse, but its wire and receiver work still multiplied badly across
long transfers. Every ranged response copied the complete target manifest even
when the same live receiver had already validated and retained it. At the 4 TiB
payload frontier the canonical manifest contains 4,096 SHA-256 strings. A 4 MiB
range walk has 1,048,576 responses, so repeating only the 8-byte length and
64-byte text for every digest after the first response admits at least
309,237,350,400 avoidable wire bytes: just under 288 GiB, before optional-field
and manifest framing overhead.

The receiver also rebuilt and sorted a 4,096-entry predecessor digest index at
every later delta-eligible block boundary. That work was formally bounded but
needlessly repeated. Both multipliers conflict with the required multi-terabyte
Linux workflow and with the user's explicit concern about memory and delta
performance.

## Reconciliation protocol generation 5

Rev0992 advances reconciliation framing and structural digests from generation
4 to generation 5. A ranged payload now always carries a canonical
`fixed_block_manifest_digest`. The digest binds:

- a domain-separated manifest generation;
- the complete payload SHA-256;
- the complete payload extent;
- the canonical fixed block size;
- the exact block count; and
- every block SHA-256 in canonical order.

An initial or cache-cold continuation request carries no manifest-cache claim,
so the response must include both the digest and complete manifest. After the
receiver has retained that exact manifest in the same service process, its next
continuation request may advertise the digest. The source must then return the
same digest and omit the complete manifest. Sending a full manifest in response
to a cache claim, omitting one without a cache claim, or changing the digest
fails cross-message validation.

This is not durable authority. A new service process has no target-manifest
cache and therefore cannot advertise one. It automatically receives the
complete manifest again before any local predecessor reuse can depend on it.
The continuation still binds the exact operation ID, content SHA-256, complete
extent, next byte offset, source evidence-set digest, selective-sync policy,
actors, folder, and authenticated channel.

## Source-side authority and bounded work

One authenticated serve session may retain one complete verified payload-store
snapshot and one target manifest. Even when a receiver advertises a cached
manifest digest, the source first computes or reuses its own complete manifest
for the current immutable payload and compares the exact digest. Only then does
it emit a reference-only range. This prevents a receiver-provided digest from
becoming source content authority.

The source records separate counters for:

- complete payload snapshot scans and reuses;
- fixed-block manifest scans and process-local reuses;
- bytes hashed while producing manifests;
- complete manifest publications; and
- digest-only manifest references.

The change removes repeated serialization and copying. It does not remove the
one complete source hash pass required to construct a manifest in a new serve
session.

## Receiver-side target cache

The receiver retains one `CachedTargetFixedBlockManifest` containing the exact
operation ID, content SHA-256, total extent, manifest digest, and complete
manifest. `make_request_or_throw` advertises the digest only when the supplied
payload continuation matches all of those target fields. An externally forged
request object cannot lend cache authority to `apply_response_or_throw`: a
reference-only response is rejected unless the actual receiving service owns
the exact cache.

The pure protocol can verify the reference digest and request binding but cannot
see process memory. The service therefore performs the remaining semantic
check. For a complete fixed block it compares the received chunk digest with
the retained target block digest before staging any bytes. A focused regression
changes a full referenced block and its chunk digest together, proves the pure
frame remains structurally coherent, and requires service rejection while the
durable prefix remains unchanged.

## Receiver-side predecessor index refactor

The predecessor acceleration cache is now one cohesive
`CachedPredecessorFixedBlockManifest` rather than parallel optional fields. It
binds the target operation, predecessor operation, exact predecessor manifest,
and one vector of block indices sorted by `(digest, original index)`.

The sorted index is built only when a new predecessor manifest is hashed. Later
eligible target block boundaries reuse the same vector for `lower_bound`; they
do not allocate, fill, and sort another 4,096-entry vector. The cache is cleared
as one unit when the target changes, the source cutpoint changes, or the target
payload completes. Payload bytes are still reopened through targeted
payload-store authority and re-proved before each local copy.

## Runtime proof

Focused C++ tests prove:

- generation-5 request and response round trips;
- full-manifest bootstrap and digest-only continuation;
- invalid, missing, noncanonical, or mismatched manifest authority fails closed;
- a 4 TiB logical shape uses the canonical 4,096-block manifest;
- reference-only framing removes more than 256 GiB of repeated manifest bytes
  over 1,048,576 uninterrupted 4 MiB ranges;
- a live three-block delta transfer publishes one target manifest, references it
  once, hashes one predecessor manifest, builds one sorted predecessor index,
  and reuses both on the next range;
- a receiver service restart omits the cache claim and obtains a complete
  manifest again;
- subsequent same-process continuation returns to reference-only framing; and
- a forged referenced full block cannot alter the staged prefix.

TLS accounting proves the same full/reference transitions survive the real
bounded record exchange.

## Memory boundary

The retained receiver state is bounded by one target manifest, one predecessor
manifest, and one 4,096-entry `size_t` index. A cache-cold decoded response may
temporarily contain another target-manifest copy while it is installed. The
source serve session retains one target manifest. None of these structures grow
with tree path count or total retained history.

This is still not a measured peak-RSS result for a real multi-terabyte tree.
The string representation is also not the densest possible manifest encoding.
A binary digest vector or a hierarchical manifest may reduce bootstrap bytes and
allocations further.

## Deliberate limitations

Rev0992 remains fixed-block delta. Insertions near the beginning of a large file
can shift block boundaries and defeat reuse. It does not provide content-defined
chunking, a multi-level manifest, cross-file block discovery, durable manifest
caches, compression, automatic sparse-file semantics, Android storage adapters,
rename/move identity, or a target-scale soak result.

The next delta product edge should be an insertion-resilient design that keeps
memory bounded and supports progressive discovery, rather than requiring a
second whole-file-sized metadata structure. In parallel, the generated
multi-terabyte-shape harness should measure peak RSS, indexing time, catch-up,
SQLite growth, payload amplification, restart, and controlled ENOSPC.

## Validation

Exact rev0992 source passed the GCC 14.2 Debug 340-edge rebuild to a no-work bundled-SQLite re-attestation, all 271/271 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 4,891 reconciliation-protocol, 109 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, and 448/448 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 98 network-model checks plus 41 generated operations, 26 selective-policy, 4,891 protocol, 361 SQLite-owner, 238 prepared-publication, 536 folder-owner, 109 service, and 2,044 TLS checks; the folder-owner proof peaked at 1,689,104 KiB RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0991 parent SHA-256 matched ac2c873d6828d1421a7c0e637ba7efa49dce62f59e7f7dbcf8e9c40d1398016c and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 597 files / 27,777,046 bytes with SHA-256 25a5beffcc7792c5a6a96e42e85803597a67f56d7eb6b67f0a617ad3397a565d.

## Archive

AnonSync-rev0992-2026.08.04.13.20-manifestreference-indexcache-restartbootstrap-sodalite.zip
sodalite
