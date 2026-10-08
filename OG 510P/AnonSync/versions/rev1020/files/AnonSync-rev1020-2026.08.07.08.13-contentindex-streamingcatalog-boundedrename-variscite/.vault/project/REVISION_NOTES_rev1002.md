# AnonSync rev1002 revision notes

## Summary

Rev1002 keeps reconciliation protocol generation 7 and bounds local delta-copy
source reads to 32 MiB per apply across same-path predecessor and cross-file
reuse. Exact durable-prefix continuation resumes inside one adaptive chunk,
including after reconstruction of the reconciliation service, while already
framed wire suffixes are preserved.

## C++ changes

- Added one shipping 32 MiB local-reuse source-read frontier per apply.
- Shared that frontier across predecessor and cross-file candidate reuse.
- Charged actual candidate bytes read, not only bytes newly accepted by staging.
- Located the adaptive chunk containing the durable target prefix instead of
  requiring an exact chunk-boundary entry.
- Added exact intra-chunk source offsets and restart-safe continuation through
  the existing durable staged prefix.
- Added a product-owned four-MiB local-copy range independent of wire framing.
- Suppressed further local reads after exhaustion while continuing to consume
  every already authenticated range in the bounded response.
- Accounted fully covered wire ranges and retained partially overlapping suffixes
  by hashing and staging only the advancing bytes.
- Added local read-range, read-byte, maximum-range, exhaustion,
  interior-resumption, already-durable-wire, and overlap-trim counters through
  the service, TLS aggregation, `anonsync_sync`, and `anonsync_replica` JSON.
- Declared the reconciliation service's direct SHA-256 link instead of relying
  on a transitive payload-store implementation dependency.
- Added constructor-bound test control while preventing callers from raising the
  shipping frontier.

## Runtime regression

A deterministic 24 MiB predecessor and 256 KiB insertion produce a matching
adaptive chunk larger than the one-MiB test frontier. The source preframes three
768 KiB ranges per response, forcing one local copy to cross a wire boundary.
The receiver reconstructs its service after the first exhaustion, resumes inside
the same adaptive chunk, preserves a partially overlapping authenticated suffix,
proves exact wire/staged/reused accounting, reduces network bytes, and converges
exact bytes and causal evidence. The focused executable passes **185 checks** on
the reviewed source before release sealing.

## Adjacent audit and refactor

The first implementation coupled local ranges to negotiated wire framing, which
left a syscall and durability-effect multiplier. The next bounded version broke
out of the wire loop at exhaustion, potentially discarding many already received
bytes. The retained design keeps the four-MiB local range and trims only the
exact already durable prefix from later wire ranges.

A competing unsealed rev1002 prototype and build were excluded. Its relevant
three-file source reference was preserved externally with an explicit
non-authority marker before the prototype tree and build cache were removed.

The full registry exposed two inherited lexical audits that encoded superseded
implementation spelling: exact-boundary-only local reuse and universal overlap
rejection. They now require the shared shifted/interior-resumable copy path,
complete-range replay accounting, advancing-suffix preservation, and terminal
gap rejection without weakening the runtime or protocol oracles.

## Product boundary

This bounds matched-candidate copy reads, not all local I/O in an apply. A
same-path predecessor manifest can still require a complete source hash, and
terminal staged-prefix completion can still rehash the complete target in one
owner call. Cross-file projection retains an independent 32 MiB frontier. No
durable global chunk index, target-scale sparse multi-terabyte measurement,
identity-preserving rename/move, Android adapter, selective-sync placeholder,
automatic eviction, polished conflict workflow, best-effort collector, ENOSPC
qualification, or live public-route proof is added.

## Release cutpoint

Validation: `Exact rev1002 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 285/285 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 185 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 31/31 bounded local reuse, 32/32 bounded resumable cross-file projection, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, and 538/538 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 185 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 30.21 seconds at 1,694,316 KiB peak RSS, the reconciliation-service proof in 21.07 seconds at 778,188 KiB, and the payload-store proof in 9.47 seconds at 519,228 KiB. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1001 parent SHA-256 matched f5f7313ecd228074cd040cf432305626aa2654e4d936c125ec4daa26098b2de4 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete 613-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 613 files / 28,332,387 bytes with SHA-256 adcc77e2efda814bfb8d69cfd03ee289ba7077085cd3fa6a6c44e45d90cd4374. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished scratch worktrees, the divergent unsealed local-copy prototype, an interrupted aggregate sanitizer shard, the pre-build missing-target invocation, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.`

Archive: `AnonSync-rev1002-2026.08.05.11.19-localcopyfrontier-interiorresume-wireoverlap-sinhalite.zip`

Codename: `sinhalite`
