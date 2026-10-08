# Rev0960 audit

## Mission

AnonSync remains one open C++ replacement for practical Resilio Sync workflows.
Rev0960 adds an owner-triggered complete current-byte proof without creating a
second synchronization engine or bypassing ordinary convergence.

## Primary implementation slice

The shipping CLI admits exactly `recheck\n` over the retained owner-only local
socket and returns a PID-bound process-local generation. The payload store's
complete rooted scanner disables process-local and durable verification reuse,
asserts exact hash totals, and hands the same move-only snapshot into the existing
folder convergence owner. Lease contention and stable corruption retain the same
service process and pending request; recovery requires current bytes plus ordinary
convergence. Status schema v7 exposes request, work, handoff, retry, and recovery
state.

## Adjacent audit and refactor

The control path now has one mutex-linearized action state, one owner observation,
one wait predicate, and an owner shutdown seal. The old split getters and redundant
atomic shadow state were removed. Terminal JSON parsers reject duplicate keys. The
release verifier's duplicated rev0960 policy branch was collapsed and is now
structurally required to occur exactly once. A corruption oracle no longer assumes
`readdir` ordering.

## Evidence

- GCC: fresh 527-edge graph; 258/258 registry; independent 39/39 product lane.
- Clang 17 ASan/UBSan: fresh 238-edge graph; 39/39 product tests with leak detection.
- Focused matrix: 84 SHA, 19 scrub-state, 26 verification-index, 519 payload-store,
  30 POSIX, 92 network-model plus 41 generated operations, 296 SQLite-owner, 360
  folder-owner, 110 sync-once, 2043 TLS, 17 integrity-evidence, and 69 local-socket
  checks.
- Structural audit: 166/166.
- Parent package: exact SHA-256 and 41/41 checks.
- Source reconstruction: 16/16 active files exact by bytes and mode.
- Active projection: 567 files, 25,420,532 bytes, SHA-256
  `61fed36a59412827b9aec3e5d6604c37fecf5107de647cadef28422bf4086788`.

## Boundaries

This is not a durable request queue, subpath scanner, live progress stream,
filesystem-wide scrub, quarantine/restore/versioning/garbage-collection policy,
hostile same-UID defense, portable Unix-socket security proof, universal
power-loss qualification, or completion of a measured Resilio uninstall workload.
