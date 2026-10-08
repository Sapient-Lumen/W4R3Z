# AnonSync rev0905 implementation and release audit

## Heart of the mission

AnonSync is an evidence-authorized, crash-consistent, bounded convergence engine under construction. Exact validated history and trust state authorize operations; summaries, cursors, clocks, leases, pathnames, transport sessions, build metadata, and status output may accelerate or report work but must not silently create authority or a newer cutpoint.

## Corrected severe failure

ASan found an operational SQLite VFS heap-buffer-overflow. The wrapper delegated an ordinary `std::string::c_str()` pathname to SQLite's Unix VFS, which retained it and later interpreted it as SQLite's extended `sqlite3_filename` family during WAL shared-memory initialization. Rev0905 owns one `sqlite3_create_filename()` family for the main, journal, and WAL names, delegates only official database/journal/WAL views, and frees the family only after all wrapped files close and the private VFS is unregistered. The retained failing sanitizer transcript is evidence, not a passing claim.

## Removed waste and authority inflation

Product `status` formerly instantiated write-capable operational owners and could reconcile durable profiles, recover or checkpoint SQLite, create sidecars, and synchronize payload bytes and directories. Rev0905 gives status explicit read-only exact-schema observers. WAL state is copied under before/after identity checks into a bounded anonymous memfd, its WAL index remains connection-local, persistent mmap/shared-memory and mutating file controls are structurally unavailable, and payload inspection uses a shared non-synchronizing lease. Process adversaries compare deployment files and directory metadata before and after observation.

## Build-authority refactor

A single CMake profile now binds the exact bundled SQLite inventory, hashes, semantic version, source ID, native configure gate, always-run build gate, generated private constants, and live runtime attestation. Active implementation projection v3 includes `cmake/`, closing the previous omission of executable build authority. Runtime evidence fields use process-lifetime `std::string_view` values rather than repeated heap-backed copies.

## Validation

- GCC 14 Debug registry: 226/226.
- Clang 17 Debug registry: 226/226.
- Strict focused GCC ASan/UBSan lane: 4/4 after repair.
- Direct descriptor-rooted SQLite process authority: 103/103.
- Database-open source audit v18: 37/37.
- Bundled profile clean/adversarial: 10/10 and 10/10.
- Native build gate: 7/7.
- Active projection policy: 7/7.
- Parent rev0904 package: 31/31 under the rev0905 verifier.
- Cumulative changeset reconstruction: 6292/6292 files byte/mode-identical.

## Remaining product gaps

The largest missing piece is still one bounded long-running supervisor and an end-to-end causal loop that continuously discovers authorized filesystem evidence, exchanges manifests, streams resumable chunks, applies conflict policy and effects, recovers crashes, quarantines invalid state, and performs retention/GC under explicit resource budgets. Cross-store atomicity, at-rest encryption and key lifecycle, durable indexes, formal privacy and traffic-analysis claims, external builder provenance, signatures, transparency-log identity, and native non-Linux descriptor authority remain outside this revision.

## Bound source identity

- Parent archive: `AnonSync-rev0904-2026.07.26.05.38-locksafevfs-mountfamily-readinesscutpoint-jasperbridge.zip`
- Parent SHA-256: `aebc60949f519479f45ce898c469d25642373fe68f170c657cd7cdbe89aede05`
- Parent source handoff commit: `34f17075684c8fc9d8fcf2922e246208c694070b`
- Rev0905 implementation commit: `f733f6a9673cf23e4acd3f23521045686374ea4b`
- Active projection: 470 files, 21824456 bytes, `b6d75cfb3b258ab38839ad7aaa147ac9030a3398ee73263b8a5d4b15cec69d82`
- Changeset: 44 paths, 4077 insertions, 248 deletions, `ad42372997d232947f375faf054b1eabe0c1bb5150e82bf7766fcc70458aa2a2`
