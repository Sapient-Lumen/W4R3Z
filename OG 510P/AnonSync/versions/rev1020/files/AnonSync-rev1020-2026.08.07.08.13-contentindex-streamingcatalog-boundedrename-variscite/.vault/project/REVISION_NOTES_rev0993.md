# Revision notes — rev0993

## Product move

Rev0993 removes the complete retained-payload namespace from ordinary source
reconciliation. Every payload-bearing request now creates one request-scoped
exact-name targeted access, opens only the selected digest under the current
store identity and lease, consumes its bytes immediately, and releases every
namespace-wide capability before the response returns.

This fixes a real same-session liveness defect. File operation evidence may be
present before its payload bytes. Rev0992 cached an absent payload behind an
unchanged evidence-set digest, so bytes that arrived later could remain invisible
until reconnect. Rev0993 never caches absence: the same authenticated serve
session sees the newly admitted payload on its next request without evidence
churn or a complete store scan.

The source session now retains only the bounded target manifest and its exact
source observation. It no longer retains a `SyncReplicaFilePayloadStoreSnapshot`
whose index and first observation scale with all retained current and historical
payload objects.

## Adjacent audit/refactor

The first targeted implementation retained access for the whole network
session. That was corrected before release because a live targeted access is
conservatively capable of reopening every current payload and therefore roots
the complete physical namespace for retention planning. The final access lives
only inside one service request and is gone before TLS output or peer wait.

Whole inline targeted copies now perform an exact complete SHA-256 comparison
and raise the typed integrity fault before corrupt bytes can be advertised.
Manifest reuse for ranged transfer additionally requires the exact canonical
POSIX source observation from the current open. Runtime proof covers late
payload arrival in the same session, unrelated namespace corruption as an
explicit nonclaim, zero retained targeted roots after return, and source-side
whole-payload corruption.

## Product boundary

This removes one namespace-sized source memory and I/O multiplier; it is not a
measured multi-terabyte peak-RSS result. Complete scans remain necessary for
namespace health, capacity, scrub, and retention duties. Fixed-block delta still
loses reuse under shifted insertions, so content-defined or multilevel delta and
a generated target-shape measurement remain open. Android, rename/move identity,
placeholders, and ENOSPC qualification are also not claimed.

See `REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md`.

## Validation

Exact rev0993 source reached a no-work GCC 14.2 Debug complete graph across four bounded resumptions with no retained compiler or linker diagnostic; all 272/272 registered tests and all 43/43 independently replayed product tests were accounted for. Focused GCC proofs passed 644 payload-store, 119 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, 33/33 targeted-source-access, and 453/453 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges and all 43/43 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed the same 644, 119, and 2,044 checks, including the 536-check folder-owner proof in the product lane. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0992 parent SHA-256 matched 2e0c19129634200ea2c1e2575e3cdcb286b46257bea2f47993558ebfdcbbca93 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 598-file projection byte-for-byte and by mode. The final active implementation projection contains 598 files / 27,812,299 bytes with SHA-256 3416936101fdc9cc2ae244bedaa39546575e9a3a52ae5c7c017fcc3d5f6af9ba. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

## Archive

AnonSync-rev0993-2026.08.04.15.02-requestscopedsource-liveavailability-retentionunroot-prehnite.zip
prehnite
