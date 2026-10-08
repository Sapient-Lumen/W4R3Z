# Revision notes — rev0992

## Product move

Rev0992 removes a severe repeated wire and CPU multiplier from the fixed-block
delta path required by the Linux multi-terabyte workflow.

Reconciliation protocol generation 5 introduces a canonical target-manifest
digest. The first range, or the first range after receiver restart, carries the
complete bounded manifest. A same-process continuation advertises the exact
digest and receives only a constant-size reference. At the 4 TiB payload
frontier, an uninterrupted 4 MiB range walk therefore avoids just under 288 GiB
of repeated digest-vector framing after the first response.

The receiver also retains the predecessor digest-order index alongside the
predecessor manifest. It hashes and sorts once per selected predecessor rather
than rebuilding a 4,096-entry index at each later delta-eligible block boundary.
The target and predecessor caches are exact, bounded, process-local acceleration
only; a restarted service automatically bootstraps a complete target manifest.

## Adjacent audit/refactor

Parallel optional cache fields were replaced by cohesive target and predecessor
cache records. This makes identity and reset behavior auditable as one unit.
The service also validates a complete referenced block against its retained
manifest before staging bytes. A negative regression changes both the wire bytes
and their chunk digest, then proves rejection leaves the durable prefix
unchanged.

## Product boundary

This does not solve insertion-shift behavior. Fixed blocks remain a first delta
generation, not content-defined chunking. The source still hashes a complete
large payload once in a new serve session, and a restarted receiver receives one
complete manifest again. No real multi-terabyte byte soak, Android port,
rename/move identity, placeholder UI, or ENOSPC qualification is claimed.

The next product edge remains insertion-resilient delta plus generated
multi-terabyte-shape measurement under explicit peak-RSS and disk-amplification
accounting.

See `MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md`.

## Validation

Exact rev0992 source passed the GCC 14.2 Debug 340-edge rebuild to a no-work bundled-SQLite re-attestation, all 271/271 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 4,891 reconciliation-protocol, 109 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, and 448/448 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 98 network-model checks plus 41 generated operations, 26 selective-policy, 4,891 protocol, 361 SQLite-owner, 238 prepared-publication, 536 folder-owner, 109 service, and 2,044 TLS checks; the folder-owner proof peaked at 1,689,104 KiB RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0991 parent SHA-256 matched ac2c873d6828d1421a7c0e637ba7efa49dce62f59e7f7dbcf8e9c40d1398016c and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 597 files / 27,777,046 bytes with SHA-256 25a5beffcc7792c5a6a96e42e85803597a67f56d7eb6b67f0a617ad3397a565d.

## Archive

AnonSync-rev0992-2026.08.04.13.20-manifestreference-indexcache-restartbootstrap-sodalite.zip
sodalite
