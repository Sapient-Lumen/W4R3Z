# Rev0986 fixed-block delta and multi-terabyte capacity audit

## Product correction

The first supported product workload is now explicit: Linux/headless peers,
large media trees measured in terabytes, bounded memory independent of tree
size, mandatory selective synchronization, and mandatory delta transfer for
changed large files. Android compatibility is a desired future architecture
constraint, not a rev0986 support claim. Credentials and private keys remain
operator-owned and outside AnonSync backup authority.

Rev0986 moves the shipping reconciliation protocol from whole-file range resume
to its first actual delta-transfer generation. A changed file still has one
canonical whole-file SHA-256 identity, but every ranged response now carries a
complete bounded fixed-block manifest. The receiver can fill the existing
crash-safe contiguous prefix from an exact retained causal predecessor before
requesting more network bytes.

This is a production C++ path, not a detached experiment. It is used by the
same reconciliation service, TLS exchange, one-shot sync, and retained peer
service that already admit authenticated remote operations.

## Bounded manifest

Protocol generation 3 uses a canonical power-of-two block size chosen from
4 MiB through 1 GiB. The smallest size that keeps the complete file at or below
4,096 blocks is selected. The resulting examples are:

| Complete file extent | Canonical block size | Maximum retained hashes |
|---:|---:|---:|
| up to 16 GiB | 4 MiB | 4,096 |
| 64 GiB | 16 MiB | 4,096 |
| 4 TiB | 1 GiB | 4,096 |

The active manifest bound is per file, not per tree. The source serve session
retains at most one ranged-file manifest and the receiver retains at most one
predecessor manifest for its current target operation. Each manifest currently
uses a bounded `std::vector<std::string>` of lowercase SHA-256 text. That is a
constant digest-count bound, not a claim about exact allocator overhead or
whole-process RSS.

Every ranged payload carries the complete manifest, so a restarted receiver
does not depend on an ephemeral prior plan before requesting a later range.
Protocol validation requires:

- the canonical block size for the complete extent;
- exactly enough hashes to cover the file;
- lowercase SHA-256 text for every block;
- a range wholly contained in one manifest block; and
- agreement between a complete block range and its manifest hash.

Whole-file payloads are intentionally not burdened with a manifest. The
response-frame bound charges one maximum manifest because a validated page may
contain at most one ranged payload.

## Exact predecessor reuse

The receiver considers only operation IDs explicitly named in the successor's
`predecessor_operation_ids`. A candidate must be a retained file operation for
the exact same canonical path and a different content digest. It is opened
through the existing targeted payload-store authority, which independently
re-proves the digest-named immutable object and current store identity.

The predecessor is streamed once to construct the same bounded block
projection. A sorted vector of block indices provides digest lookup without
copying another set of digest strings. Matching requires both block SHA-256 and
exact block length, allowing an unchanged block to be reused from a different
offset when fixed block boundaries happen to align.

Each matching predecessor range is reopened and copied with `pread(2)` through
the ordinary bounded wire-range ceiling. The descriptor-owning capability is
released before the bytes enter mutable prefix staging, preserving the store's
reader/writer lease order. Reused bytes enter the existing durable contiguous
prefix journal. If reuse stops at the first missing block, the next ordinary
network range starts from that exact durable prefix.

No remote file operation is admitted merely because block hashes matched. The
complete reconstructed digest-named payload must become durable and pass the
existing whole-file SHA-256 proof first. A crash can leave resumable private
bytes, but cannot leave visible operation metadata ahead of its payload.

## End-to-end regression

The focused reconciliation-service regression uses a 12 MiB file split into
three 4 MiB blocks.

1. A successor changes the first byte of the first two blocks. Two bounded
   network pages transmit 8 MiB, one 4 MiB predecessor block is reused locally,
   and both source and receiver hash their active manifests once across the two
   pages.
2. A later successor changes one byte only in the first block. The source sends
   4 MiB, the receiver reuses the remaining 8 MiB as two predecessor blocks,
   the exact complete bytes are admitted, and no continuation remains.

The regression proves the required product distinction: range resume alone
would still transfer the full changed file, while fixed-block delta avoids
network transfer for unchanged aligned blocks.

## Operator accounting

The source reports fixed-block manifest scans, cache reuses, and hashed bytes.
The receiver reports locally reused blocks, ranges, and bytes plus predecessor
manifest scans, cache reuses, and hashed bytes. These counters propagate through
the TLS exchange and the shipping low-level and one-shot JSON surfaces. They
are diagnostics, not admission authority.

## Multi-terabyte capacity correction

The delta manifest exposed a severe hidden capacity contradiction. The wire
format could describe a multi-terabyte file, but the deployment manifest
rejected files above 4 GiB and the production payload-store aggregate ceiling
remained 64 GiB. A valid media tree could therefore be structurally impossible
to synchronize even though all actual reads and writes were streamed.

Rev0986 centralizes the complete-file extent policy:

- new deployments default to a 64 GiB per-file ceiling;
- an operator may select up to 4 TiB per file, exactly matching the bounded
  manifest frontier; and
- the production store uses `9007199254740991` bytes (8 PiB minus one) as an
  exact aggregate comparison frontier.

The aggregate value is the largest integer exactly representable in ordinary
JSON number semantics. It is not a quota, allocation request, file-size
reservation, or promise that a filesystem has that capacity. No buffer or
container is sized from it. Actual retained bytes remain bounded by the selected
filesystem, quota, free space, the still-explicit 100,000-payload identity
frontier, and future best-effort retention policy.

The per-file transient frontier remains twice the selected payload ceiling so
one crash-safe assembly and one bounded publication/reproof path can coexist.
Wire buffers remain 4 MiB by default.

## Research comparison

Syncthing's current Block Exchange Protocol also chooses a power-of-two fixed
block size from the complete file extent, targeting fewer than 2,000 blocks and
using blocks from 128 KiB through 16 MiB. Rev0986 deliberately chooses a much
smaller maximum digest count and therefore coarser blocks for very large files.
That is a memory-first first generation, not an assertion that AnonSync's
tradeoff is universally better. See:
https://docs.syncthing.net/specs/bep-v1.html#selection-of-block-size

Android remains a separate portability problem. Android's Storage Access
Framework can grant a user-selected directory tree, while scoped-storage and
foreground-service rules do not provide the same unrestricted rooted POSIX
namespace and continuously running daemon assumptions used by the Linux owner.
A Termux or app-private-storage experiment may validate the portable C++ core,
but a supported Android product needs explicit storage and lifecycle adapters.
See:
https://developer.android.com/training/data-storage/shared/documents-files
https://developer.android.com/develop/background-work/services/fgs

## Deliberate limitations

Rev0986 does not provide content-defined chunking. An insertion near the start
of a file shifts later fixed boundaries and may destroy most reuse. It also does
not search every retained historical version for an optimal block source; it
uses the first exact retained direct causal predecessor that can be opened.
Peers using protocol generation 2 cannot reconcile with generation 3 and must
be upgraded together.

Selective synchronization is still missing and is the next existential product
slice. Android is not supported. Rename/move identity, empty directories,
portable metadata, ordinary conflict presentation, quota/ENOSPC behavior, and
best-effort retention collection remain open. The fixed-block seam is designed
so a later content-defined or multi-level signature can replace the manifest
without creating a second payload-admission engine.

## Evidence boundary

`tests/sync_replica_reconciliation_service_test.cpp` is the focused semantic
oracle for local block reuse and exact final convergence. Protocol, payload
store, TLS, deployment-manifest, folder-owner, full product, and sanitizer tests
remain independently load-bearing.

`tools/audit_sync_replica_fixed_block_delta.py` is a lexical source-shape audit.
It cannot prove cryptography, POSIX identity, durability, allocation success,
crash recovery, wire privacy, performance on a real multi-terabyte tree, or
Android behavior.
