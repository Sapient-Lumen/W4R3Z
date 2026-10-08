# Request-scoped targeted source access audit — rev0993

## Product defect

Rev0992 made fixed-block continuation framing and predecessor lookup bounded,
but the source side still constructed and retained one complete payload-store
snapshot for every payload-bearing authenticated serve session. That snapshot
walks the complete private payload namespace, validates every entry, retains a
`PayloadIndexEntry` and content-inventory identity for every payload, and hashes
any cold or changed object. Serving one selected file therefore inherited work
and retained memory proportional to all current and historical payload objects.
That is the wrong multiplier for the required Linux multi-terabyte media-tree
workflow.

The ownership was also semantically stale. Operation evidence and payload bytes
are admitted through separate crash-safe steps. A source may legitimately hold
one file operation while its payload is temporarily absent, then receive the
payload later without changing the operation evidence set. Rev0992 keyed its
session snapshot reuse only to the evidence-set digest. Once that snapshot had
reported the payload absent, the same live authenticated session could continue
returning `PayloadUnavailable` forever even after exact bytes arrived. A
reconnect happened to clear the stale negative observation, but reconnect is not
part of file-availability authority.

## Retained correction

A payload-bearing source request now creates one
`SyncReplicaFilePayloadStoreTargetedAccess` local to
`serve_request_or_throw()`. The access performs identity reconciliation and
rooted setup once for that bounded request, but it does not enumerate the
payload namespace. Every materialized file operation is opened by its exact
lowercase SHA-256 basename under a fresh fail-fast shared store lease. Current
absence returns `PayloadUnavailable` for that exact operation. Presence yields
one descriptor-owning payload capability for immediate byte consumption.

The access is destroyed before the response leaves the service call. No payload
descriptor, store-wide lease, targeted-access registration, or
all-current-payload retention root survives the subsequent TLS write or peer
wait. This request scope matters: the first draft retained targeted access in
the long-lived serve session. Retention planning correctly treats any live
targeted access as capable of reopening every current payload. Keeping one for
the life of a network session would therefore have conservatively rooted the
whole physical payload namespace and could have defeated future collection
while an ordinary peer remained connected. The reviewed implementation retains
only manifest acceleration in the session.

## Current availability and stale-negative removal

Each later request performs a new exact-name open. The source does not cache
absence. A focused regression:

1. admits file operation evidence without its payload;
2. serves one `PayloadUnavailable` response;
3. publishes the exact payload without changing the evidence set;
4. reuses the same authenticated source serve session and continuation; and
5. receives and applies the file normally.

The session reports two request-scoped access births, two exact-name attempts,
and one successful open. Reconnect, evidence churn, and a complete namespace
scan are not required to make later bytes visible.

## Namespace-health nonclaim

Targeted access proves only the selected name at one lease/root cutpoint. It
never claims that unrelated payload-root entries are valid, that the namespace
fits configured entry or byte capacity, that no stale transient object exists,
or that the complete retained inventory is healthy.

The regression places an invalid unrelated regular file beside one valid
selected digest. Source reconciliation serves the valid digest successfully.
A subsequent complete `snapshot_or_throw()` rejects the unexpected entry. After
the invalid entry is removed, an independent live-capability cutpoint proves
that the completed serve call left `targeted_access_count == 0` and did not
leave an all-current-payload root. The complete snapshot remains the sole
namespace-health, capacity, transient-state, and complete-inventory oracle.

## Byte proof

The old complete snapshot had already hashed every cold or changed payload.
Targeted selection intentionally does not prehash the chosen file, so the byte
consumer must provide the content proof.

For whole inline payloads, `copy_range_or_throw()` now recognizes an exact
whole-file range, hashes every returned byte, compares the result with the
SHA-256 basename bound by the operation, records the process integrity fault on
mismatch, and throws the typed payload-integrity exception before any response
can advertise the corrupt bytes. Exact empty payloads are valid whole ranges;
nonempty end offsets remain invalid.

For ranged payloads, a cache-cold target-manifest construction streams and
hashes the complete selected descriptor. Later manifest reuse is allowed only
when content digest, extent, block size, and the complete canonical eleven-field
POSIX source observation exactly match the newly opened payload. The current
range is then copied from that same descriptor and re-proved after reading. The
receiver continues to validate complete block bytes against the retained target
manifest before staging and to verify the final assembled payload before
admission.

This does not claim protection from a noncooperating privileged writer that can
change bytes while restoring every compared observation, nor does it replace the
rotating scrub and complete namespace scan.

## Memory and work boundary

The source serve session no longer retains `SyncReplicaFilePayloadStoreSnapshot`
or its payload-index and content-inventory vectors. Session memory is bounded by
one canonical target manifest (at most 4,096 block digests), fixed-width source
metadata, channel identity, and counters. Each request additionally holds at
most one targeted root capability and one opened payload descriptor at a time,
plus the already bounded response payload bytes.

This removes source-session state and first-request traversal proportional to
the complete retained payload namespace. It is not a measured target-scale RSS
claim. The payload store still has process-wide verification acceleration,
complete scans still scale with the physical namespace when their actual health
or retention duties require them, and one request may still serve several
bounded file operations.

## Telemetry

The source session, TLS exchange result, and shipping diagnostic JSON now expose:

- request-scoped targeted-access births;
- exact payload-open attempts;
- successful exact payload opens;
- target-manifest scans and reuses;
- bytes hashed for target manifests; and
- full-manifest publications and digest-only references.

The removed snapshot scan/reuse counters are not silently reinterpreted. An
access birth is one bounded request preflight, not a namespace scan and not a
content proof.

## Adjacent audit/refactor

The review corrected the first implementation rather than sealing it:

- session-scoped targeted access was reduced to request scope after the
  retention-root consequence was traced;
- stale snapshot metrics were replaced with exact access/open metrics;
- the payload-store targeted-access comment now names both legitimate absence
  consumers and the retention-lifetime consequence;
- the rev0992 manifest-reference audit was updated to bind the revised runtime
  wording without weakening its restart-bootstrap requirement; and
- a test-only private bridge proves the completed request leaves no hidden
  namespace-wide live capability.

## Product boundary and next edge

Rev0993 makes source serving path-local and current, but it does not make the
delta algorithm insertion-resilient. Fixed 4 MiB–1 GiB blocks can still lose
reuse after a small insertion near the front of a large file. It also does not
supply cross-file block discovery, target-scale peak-RSS measurements,
placeholders, Android lifecycle integration, rename/move identity, or ENOSPC
qualification.

The next scale step remains a generated multi-terabyte-shaped Linux workload
with explicit peak RSS, disk amplification, restart, catch-up, and controlled
ENOSPC evidence, followed by content-defined or multilevel delta selected from
that measurement rather than another unmeasured generalized subsystem.

## Validation

Exact rev0993 source reached a no-work GCC 14.2 Debug complete graph across four bounded resumptions with no retained compiler or linker diagnostic; all 272/272 registered tests and all 43/43 independently replayed product tests were accounted for. Focused GCC proofs passed 644 payload-store, 119 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, 33/33 targeted-source-access, and 453/453 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges and all 43/43 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed the same 644, 119, and 2,044 checks, including the 536-check folder-owner proof in the product lane. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0992 parent SHA-256 matched 2e0c19129634200ea2c1e2575e3cdcb286b46257bea2f47993558ebfdcbbca93 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 598-file projection byte-for-byte and by mode. The final active implementation projection contains 598 files / 27,812,299 bytes with SHA-256 3416936101fdc9cc2ae244bedaa39546575e9a3a52ae5c7c017fcc3d5f6af9ba. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

## Archive

AnonSync-rev0993-2026.08.04.15.02-requestscopedsource-liveavailability-retentionunroot-prehnite.zip
prehnite
