# toxsync changelog

## Unreleased hardening

- Made exact retained-publication retries restart-safe: retained inputs now land as one atomic
  directory and a pre-existing revision is accepted only after exact shape, size, and signed-HEAD
  digest validation.
- Corrected online-source accounting when an existing offline content source is re-added.
- Made Unix `head-keygen` outputs kernel-exclusively no-clobber with exact permissions and rollback
  of a newly created private half when public-key creation fails.
- Added a backend-aware command-level CTest transaction and expanded the native registry to 125
  checks; portable builtin-SHA builds still exercise content/range reconstruction without claiming
  Ed25519.
- Hardened test workspaces against predictable-name collisions and corrected two fixtures that had
  not actually exercised their advertised staging/spill conditions.

## 0.7.0 — rev0010

- Added strict fixed-size HEAD summary, query, and receipt codecs for reconnect anti-entropy without
  transferring a complete signed HEAD when both peers are already current.
- Added an atomic publication transaction: deterministic treepack, paged content-store commit,
  linked Ed25519 HEAD construction, optional retained source artifacts, and HEAD publication last.
- Added verified treepack activation into immutable revision directories, restart-safe activation
  receipts, collision rejection, and an atomic relative `current` switch with previous-target
  reporting.
- Replaced all-entry treepack path retention with caller-bounded external sort runs and bounded
  multi-pass merge while preserving byte-identical canonical output.
- Added cooperative cancellation checkpoints to long reconstruction/publication operations.
- Added lane backoff and verified useful-byte/time observation inputs for live policy engines.
- Expanded native coverage for forced spill/merge, linked publication generations, activation
  restart and collision behavior, anti-entropy records, cancellation, and resource boundaries.
- Preserved every range-v1 and paged content-v2 on-disk format from 0.6.0.

## 0.6.0 — rev0009

- Removed the provisional fixed 32-peer/32-lane scheduler policy.
- Preserved the compact <=32-peer inline mask and added a preallocated dynamic availability bitset
  using `ceil(maximum_peers / 64)` words per active object.
- Decoupled request-correlation memory from `maximum_peers * maximum_lanes_per_peer` through a
  global in-flight request budget.
- Added caller-visible availability-word/byte accounting and constructor-time workspace rejection.
- Added resource-derived lane admission from requested width, peer advertisement, transport/global
  slots, descriptor/queue budgets, and remaining memory.
- Added an allocation-free goodput lane tuner that scales beyond 32 and backs off on retry/stall
  pressure.
- Extended capability codec tests and the fabric benchmark across inline and dynamic peer profiles.
- Integrated the transport-neutral content fabric into the IoTox rev0010 one-binary coordinator and
  exercised two-source verification failure and failover.

## 0.5.0 — rev0008

- Added paged v2 root and page objects so workers can inspect and schedule bounded windows without retaining a complete chunk list.
- Added caller-bounded flat/paged chunk-window reads, including sequential offset hints for flat manifests.
- Added exact inventory pages, a compact conservative availability sketch, and capability negotiation bytes.
- Added allocation-stable dynamic and rarest-first multi-source schedulers with lane limits, retries, failover, and borrowed-window storage.
- Transposed exact peer availability into one 32-bit mask per active chunk, eliminating the peer-by-chunk bitmap and making rarity/capacity selection popcount-and-mask operations and adding a fixed-capacity rarest-first heap with linear rebuilds.
- Added a bounded transport-neutral `ContentFabricSession` that acquires paged metadata first, advances through chunk windows, installs verified objects, survives restart by rescanning the immutable store, and reconstructs only after complete coverage.
- Added verified content-object ingest with hard-link publication, bounded cross-filesystem copy, no-clobber races, and existing-object verification.
- Added Ed25519 mutable HEAD generation/signing/verification and strict linked-history policy when OpenSSL is available.
- Added checksum-protected pin journals, torn-tail repair, compaction, paged reachability marking, conservative bounded-memory garbage collection, and dry-run accounting.
- Added paged-fabric CLI operations, native benchmark, integrated fuzz inputs, and expanded native C++ tests.
- Preserved v1 index compatibility and flat v2 manifest readability.

# Changelog

## 0.4.0 — rev0007

- Added reusable, page-rounded v1 index and reconstruction workspaces with explicit resident
  bytes and allocation-growth counters.
- Replaced cursor-based large-sync streams with bounded positional file-descriptor I/O and
  optional sequential/cache-discard advice.
- Added strict fixed-size mutable-head, capability, range request, range offer, cancellation,
  and result codecs for the IoTox transport adapter.
- Added a transport-independent v2 preview with Gear content-defined chunking, SHA-256 chunk
  identities, compact flat manifests, and a content-addressed local store.
- Added atomic no-replace chunk/manifest publication, streamed missing inventory, per-chunk
  verification, complete-artifact verification, and atomic reconstruction.
- Added deterministic v2 chunk auto-scaling that bounds the worst-case flat manifest under a
  configured metadata budget, including a 16 TiB formula profile.
- Added tiny-buffer, prefix-insertion reuse, corruption, warm-workspace, and manifest-hardening
  tests; expanded the native suite from 52 to 68 registered tests.
- Added a native v2 content-store benchmark and documented the remaining scheduler, Merkle
  manifest, retention, and garbage-collection gates.
- Added seeded wire and manifest fuzz surfaces in the integrated IoToxsync matrix.

## 0.3.0 — rev0006

- Added byte-compatible on-disk v1 index construction with bounded buffers.
- Added automatic block-size selection under a configurable metadata budget.
- Added fixed-header/encoded-length index inspection without per-block allocation.
- Added aligned, memory-bounded reconstruction that streams records, basis bytes, missing
  ranges, output, and whole-artifact SHA-256.
- Added one-bit-per-block batch state and explicit data/index/state/range memory counters.
- Added batched `RangeSource::read_many` with a safe exact-read default implementation.
- Added resumable partial validation and atomic output publication.
- Retained adaptive and exhaustive rolling planning for shifted/reordered smaller artifacts.
- Added large-scale formula tests, 16 TiB profile coverage, and a native C++ large benchmark.
- Expanded the native C++ suite from 40 to 52 registered tests.
- Established measured gates before beginning the content-addressed v2 engine.


## 0.2.0 — rev0005

- Added adaptive aligned planning for common small in-place revisions.
- Added safe early abandonment when the aligned reuse threshold becomes impossible.
- Retained exhaustive bounded rolling search and an explicit aligned-only minimum-CPU mode.
- Replaced one-byte stream scanning with fixed-buffer positional reads.
- Added compact weak-checksum lookup storage and anchor-aware rolling skips.
- Added SSE2 and AArch64 NEON rolling-checksum initialization with a tested scalar fallback.
- Unrolled the v1 strong block hash while preserving regression vectors and index compatibility.
- Added optional OpenSSL EVP SHA-256 plus a tested project-owned C++ backend.
- Reworked index construction into one buffered pass over the target.
- Coalesced contiguous basis and source runs during reconstruction.
- Replaced per-block writes/flushes with fixed-buffer batched output.
- Added direct memory, read-call, run, write-call, and backend counters.
- Reworked the benchmark to stream fixtures and added in-place and shifted-prefix workloads.
- Expanded the native C++ test suite from 24 to 40 cases.
- Added GCC portable scalar/built-in, GCC native, and expanded Clang presets.

## 0.1.0 — rev0004

- Added deterministic v1 target indices with 64-byte headers and 24-byte block records.
- Added rolling receiver-side basis scanning with compact weak-checksum buckets.
- Added duplicate-target-block reuse and coalesced missing target ranges.
- Added transport-neutral random-access `RangeSource` and local `FileRangeSource`.
- Added resumable reconstruction, target SHA-256 verification, fsync, and atomic publication.
- Added a fixed 64-byte range-request codec suitable for a small Tox control packet.
- Added deterministic directory `treepack` artifacts with strict path and resource limits.
- Added a C++20 CLI, benchmark, 24 registered tests, Clang/GCC presets, ASan/UBSan, and Nix definitions.
- Established the v2 content-defined, content-addressed engine boundary.
