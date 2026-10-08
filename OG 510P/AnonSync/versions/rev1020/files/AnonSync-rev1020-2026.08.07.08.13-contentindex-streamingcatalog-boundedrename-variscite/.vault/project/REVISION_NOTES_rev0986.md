# AnonSync rev0986 revision notes

## Fixed-block delta transfer

Rev0986 advances reconciliation to protocol generation 3. Every ranged payload
carries one canonical complete fixed-block manifest. Blocks start at 4 MiB and
double only as needed to keep one active file at or below 4,096 SHA-256 hashes,
with a 1 GiB block and 4 TiB complete-file frontier.

The receiver uses an exact retained direct causal predecessor for the same
canonical path. Matching blocks are reopened, independently re-proved, copied
through bounded ranges, and appended to the existing crash-safe contiguous
prefix. Ordinary network ranges resume at the first miss. The whole payload
SHA-256 must become durable before remote operation metadata is admitted.

A 12 MiB end-to-end regression proves that a one-byte edit transfers one 4 MiB
block and reuses the remaining 8 MiB locally. Source and predecessor manifests
are cached across continuation pages so one large file is not rehashed once per
wire range.

## Multi-terabyte capacity

The delta audit found that the released 4 GiB deployment ceiling and 64 GiB
aggregate payload-store ceiling contradicted the stated multi-terabyte product
mission. New deployments now default to 64 GiB per file and may select up to
4 TiB. The production aggregate comparison frontier is 8 PiB minus one, the
largest exactly representable JSON integer.

These are validation ceilings, not allocations or disk reservations. Existing
wire buffers remain bounded, and the aggregate frontier does not allocate
memory proportional to the configured value. The 100,000 retained-payload
identity limit and real filesystem/quota capacity remain explicit boundaries.

## Audit/refactor

The source now caches exactly one source manifest per serve session and one
predecessor manifest per active receiver target, avoiding O(file size x page
count) rehashing. Range results move their byte and digest buffers into protocol
and prefix staging rather than copying them. Candidate lookup retains only a
bounded index vector rather than a second digest set.

The shared product extent header prevents deployment, protocol, and payload
store ceilings from drifting independently. The default reconciliation extent
now aliases the same 64 GiB product default rather than preserving a stale
64 MiB private default.

Operator JSON exposes network staging, locally reused blocks/ranges/bytes, and
source/predecessor manifest scan/reuse/hashed-byte accounting.

## Product direction

The first supported workflow is Linux/headless synchronization of large media
trees measured in terabytes. Delta transfer and selective synchronization are
mandatory. Rev0986 implements the first; selective synchronization is the next
product priority.

Android compatibility remains desirable but unclaimed. A Linux-on-Android or
Termux experiment may be useful, but a supported app needs explicit Android
storage and lifecycle adapters. Credentials and private keys remain under the
operator's control and are outside AnonSync backup authority. Retention remains
best-effort and continuity uncertainty remains conservative.

## Limitations

This is fixed-block reuse, not content-defined chunking. Insertions can shift
boundaries and cause large retransfers. The receiver uses the first usable
retained direct predecessor rather than searching all history for an optimal
source. Protocol generations 2 and 3 are intentionally incompatible; both peers
must upgrade together.

Rev0986 does not yet implement selective sync, Android support, rename/move
identity, empty-directory semantics, portable metadata, ordinary conflict UI,
quota/ENOSPC policy, or destructive retention collection.

## Validation

Exact rev0986 source passed a fresh GCC 14.2 Debug complete graph (536/536 configured build edges), 264/264 documentation-independent tests plus the finalized fixed-block delta audit for complete 265/265 registered-test accounting, and an independent 42/42 GCC product replay. Focused GCC proofs passed 30 deployment-manifest, 4,638 reconciliation-protocol, 644 payload-store, 99 reconciliation-service, 2,043 TLS-transport, 470 folder-owner, and 110 sync-once checks. Source audits passed 42/42 fixed-block delta and multi-terabyte capacity checks, 41/41 database-replacement checks, and 412/412 structural payload-store authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 42/42 product tests passed in bounded exact-source invocations with leak detection and halt-on-error. Focused sanitizer proofs passed the same 4,638 protocol, 644 payload-store, 99 reconciliation-service, 2,043 TLS, and 470 folder-owner checks; the folder-owner proof peaked at 1,485,264 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0985 parent SHA-256 matched a87f6fcd1f7ea371e0974c4b89ca097def56e07301bc3ffeb9cbe19bdf496c4c and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 23/23 changed active files and the complete 587-file projection byte-for-byte and by mode. The final active implementation projection contains 587 files / 27,271,627 bytes with SHA-256 7c706289c0b0e26d28a42d9b6c486a148044ab92c13a6cb0757696f038fbe1e2.

## Archive

AnonSync-rev0986-2026.08.03.20.41-fixedblockdelta-multiterabyte-memoryfrontier-azurite.zip
