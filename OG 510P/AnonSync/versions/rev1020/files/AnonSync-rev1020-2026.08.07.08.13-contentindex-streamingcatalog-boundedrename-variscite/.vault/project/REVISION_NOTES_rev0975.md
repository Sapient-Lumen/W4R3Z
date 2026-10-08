# AnonSync rev0975

## Page-invariant deletion-free mark witness

Rev0975 strengthens rev0974's exact physical retention plan without adding any
deletion authority.

- Replaced planner-local node-based reference storage and per-payload logarithmic
  lookup with one bounded borrowed vector, canonical sort, in-place root-mask
  fold, and linear merge against the complete physical payload inventory.
- Added `unreferenced_candidate_set_digest`, an exact page-invariant digest of
  every physical `(SHA-256, size)` object not named by retained File operations.
- Added `exact_deletion_free_mark_digest`, binding that candidate set to the
  folder, operation set, inactive evidence set, explicit pin set, visible state,
  and complete payload snapshot.
- Added explicit `durable_mark_persisted:false`; reclaim, quota, grace, writer-
  fenced collection, quarantine-for-GC, and unlink authority remain absent.
- Advanced the local response to
  `anonsync.local-retention-plan.response.v2` and live plus terminal status to
  `anonsync.peer-service.status.v20`.
- Added independent SHA-256 framing tests proving exact values and page
  invariance across complete and cursor-paginated output, plus stable and
  bounded status serialization checks.
- Audited and rejected a contaminated unsealed worktree containing an unrelated
  partially wired payload-usage prototype. The final source is reconstructed
  from the exact sealed rev0974 archive and carries only the reviewed patch.

See `PAGE_INVARIANT_DELETION_FREE_MARK_WITNESS_AUDIT_rev0975.md` for the
complexity boundary, digest framing, authority nonclaims, contamination audit,
and the durable writer-fenced collector protocol that remains future work.

## Validation

Exact rev0975 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 312/312 checks. A fresh Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 441-check folder-owner suite in 22.74 seconds at 1,418,744 KiB peak RSS and the 155-check local-control suite in 0.63 seconds at 99,008 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0974 parent SHA-256 matched 82d713da7546d14e3875e4b5beea1fb6ecb3fe4d4031e07c01ec7a10d39165f7 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 11/11 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,357,846 bytes with SHA-256 f2df82e79b066db5af8cef5545d4135e6714bbdf7cd05b1d72d6b8c069e12826. Validation excluded the contaminated unsealed payload-usage prototype, its abandoned worktree, and every result produced from it.
