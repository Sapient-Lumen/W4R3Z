# Revision notes — rev1006

## Receiver-local terminal verification

Rev1006 removes the remaining authenticated peer-turn dependency after a target
payload's complete byte prefix is already durable. A complete writable payload-
store scan now discovers exact pending terminal SHA-256 obligations from the
existing staged-prefix inode and checksum-framed journal. The retained peer
service advances one exact 32 MiB step locally, then yields at least one ordinary
owner turn before another step.

No second worker thread, queue database, hash format, or publication path was
added. Intermediate steps keep rev1005's exact-name rooted observation. Final
publication still requires the ordinary complete store scan and no-replace
rename of the exact verified staged inode.

## Bounded process state and restart

The process cache contains only digest, total extent, and verified offset for at
most the existing transient-entry frontier. It retains no payload buffers. A
fresh owner reports the observation unknown; only a complete ordinary scan can
make the cache complete. Restart reconstructs it from the durable journal and
staged-prefix namespace.

Selection is deterministic and fair by smallest verified offset, then digest.
A stale cache entry already published by another owner is reconciled without
falsely counting unperformed hash bytes.
A stale cross-process projection that cannot accept a newly committed work item
is invalidated rather than throwing after the durable effect; the next complete
store scan reconstructs it.

## Service availability and diagnostics

The receiver-local lane runs inside the existing single owner thread. It stays
subject to the shared lease, integrity, readiness, retry, drain, and shutdown
state machine. One forced ordinary turn between pulses preserves observation of
control actions, ingress, watcher/repair work, and network progress.

Status advances to `anonsync.peer-service.status.v25`. It exposes the complete
work projection, exact next obligation, seven scheduler counters, and the last
terminal step. The status renderer now fails closed on impossible aggregate,
offset, known/unknown, or empty/nonempty combinations.

The shipping process regression creates a 64 MiB-plus-4,097-byte completed
staged prefix, starts no source peer, and proves that the same ready daemon
publishes it in exactly three local pulses while its owner-only control socket
remains available.

## Sanitizer inventory correction

A clean Clang graph exposed that the new product fixture was absent from both
explicit sanitizer target inventories. Instrumented static libraries therefore
reached a fixture link that did not carry the ASan/UBSan runtime. Rev1006 adds
the fixture to both inventories and binds that two-list invariant in the focused
source audit. The pre-correction link failure is excluded from release authority.

## Adjacent audit and limitations

The focused storage regression proves restart reconstruction, deterministic
fairness between two large obligations, exact-name intermediate work in the
presence of an unrelated namespace entry, the retained complete final scan, and
zero-byte accounting when a stale process cache discovers publication by
another owner.

A 4 TiB target still requires 131,072 local 32 MiB pulses and corresponding disk
reads. Rev1006 removes peer latency from those pulses; it does not remove the
work. First discovery and final publication still perform complete store
observations. Source manifest construction and durable chunk-indexing remain
open multi-terabyte costs.

Rev1006 does not add a global chunk index, rename/move identity, full directory
semantics, Android support, selective placeholders or automatic eviction,
ENOSPC qualification, or public Tor/I2P performance proof.

## Release cutpoint

Validation: `Exact rev1006 source passed a fresh GCC 14.2 Debug complete graph with 557/557 configured build edges and exact-source no-work re-attestation; all 291/291 registered tests and the independent 49/49 product set passed. Focused GCC proofs passed 20 terminal-state-codec, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 110 sync-once, 196 reconciliation-service, and 2,044 TLS-transport checks; the shipping peer-independent scheduler process regression passed with no source peer. Source audits passed 33/33 receiver-local terminal-scheduler and 584/584 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 268/268 configured edges; all 49/49 product tests passed with leak detection and halt-on-error, and focused sanitizer payload-store proof passed all 737 checks. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1005 parent SHA-256 matched b94e3c496bbec3c230c8d3af3081f53d0f519e9945943022df80ecc3f5e3199d and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 622 files / 28,656,401 bytes with SHA-256 808d8740871083908600d243359c97e0253b456afef4ba65c5f4e88bb39e2b1f. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes the pre-correction sanitizer fixture-link failure, interrupted wrapper commands, the duplicate Ninja that briefly entered the same cache and was terminated, the remount-vanished unsealed worktree, and all obsolete validator branches and builds.`

Archive: `AnonSync-rev1006-2026.08.05.22.03-receiverlocalscheduler-restartdiscovery-ownerfairness-malachite.zip`

Codename: `malachite`
