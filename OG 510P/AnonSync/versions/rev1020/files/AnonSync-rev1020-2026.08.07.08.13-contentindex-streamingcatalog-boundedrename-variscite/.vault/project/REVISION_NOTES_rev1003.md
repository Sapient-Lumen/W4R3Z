# Revision notes — rev1003

## Bounded same-path predecessor projection

Rev1003 removes one remaining complete-source read from a single receiver apply.
Same-path predecessor content-defined projection now advances at most **32 MiB
per apply** and at most once per apply. The process-local projection retains only
bounded rolling state, completed chunk records, one digest-order index, and one
offset vector.

Completed adaptive chunks can be reused before the predecessor whole manifest
finishes. Every reused source range is still reopened, observation-reproved,
range-hashed, crash-safely staged, and covered by exact final whole-target
SHA-256 before publication. Only complete whole-source verification creates the
retained predecessor manifest and final index.

The 48 MiB shifted-insertion regression requires exactly two bounded predecessor
steps, proves no turn exceeds 32 MiB, reuses chunks during the incomplete first
step, hashes exactly the predecessor size in aggregate, lowers network bytes,
and converges exact bytes and causal evidence. The focused executable passes
**189 checks** before release sealing.

## Adjacent audit and refactor

Same-path and cross-file projections now share one incremental digest-order and
cumulative-offset index helper. This removes duplicated partial-index logic and
keeps ordering and extent invariants identical.

The audit found a failure-state mismatch: the lower payload-store projection
clears its private state on every failure, but the reconciliation service could
retain the outer offsets and digest index. Both projection paths now clear the
enclosing state at the same exception cutpoint.

The separate terminal target verification remains exact and unbounded. A
rejected prototype placed raw resumable SHA-256 state in a staged-prefix
pathname; it was excluded because it lacked an independently checksum-framed,
store-identity- and inode-bound durable authority record and safe legacy/crash
transitions. Rev1003 does not weaken final whole-target SHA-256.

## Product boundary

Incomplete predecessor progress is process-local and may be reread after service
restart. Source-side target-manifest construction and terminal staged-target
verification can still perform complete-file reads. This is not a durable or
global chunk index, a target-scale multi-terabyte measurement, a rename/move
implementation, complete directory semantics, an Android adapter, selective
placeholders or eviction, ENOSPC qualification, or live public-route proof.

## Release cutpoint

Validation: `Exact rev1003 source passed a fresh GCC 14.2 Debug graph: 262/262 product-dependency edges plus 290/290 remaining all-target edges (552/552 total), followed by bundled-SQLite re-attestation; all 286/286 registered tests and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 189 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 bounded predecessor projection, 32/32 bounded cross-file projection, 31/31 bounded local reuse, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, 21/21 bounded-history access, and 548/548 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 262/262 edges and all 47/47 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed 677 payload-store, 189 reconciliation-service, and 536 folder-owner checks, with peak RSS 519,504 KiB, 791,616 KiB, and 1,704,200 KiB respectively. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1002 parent SHA-256 matched e547cbe11ae3bae98f15946a38f30dd64881510987edac35a6c490a64220bf03 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed wrapper paths, all 13/13 changed project paths, all 10/10 changed active paths, and the complete 614-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 614 files / 28,363,976 bytes with SHA-256 16eeae537cb0683f6a51aa044b9c9aea9a44f93ced30530664b5de55cb580aa8. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded the remount-vanished initial worktree and build, the rejected raw pathname-carried SHA-state prototype, the stale non-authoritative /home/oai/share validator and its build tree, the initial unbuilt focused-sanitizer target invocation, and the superseded rev0999 lexical oracle failure before its exact cutpoint-owned lifetime check was corrected.`

Archive: `AnonSync-rev1003-2026.08.05.12.35-boundedpredecessor-partialindex-terminalfence-phenakite.zip`

Codename: `phenakite`
