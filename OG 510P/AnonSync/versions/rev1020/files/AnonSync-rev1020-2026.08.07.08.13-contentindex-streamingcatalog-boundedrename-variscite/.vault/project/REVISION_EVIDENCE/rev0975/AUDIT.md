# Rev0975 audit handoff

## Scope

Rev0975 preserves the deletion-free rev0974 retention-plan authority boundary.
It changes only the in-memory retained-reference projection, two exact output
witnesses, the v20/v2 status contracts, focused/process tests, structural
policy, and release documentation.

## Primary correction

The retention planner no longer allocates an ordered-map node per distinct
retained payload reference or performs one logarithmic map lookup for every
physical object. It builds one bounded borrowed vector, sorts by canonical
`(digest,size)`, folds root masks in place, and linearly merges with the complete
canonical payload inventory.

The plan now includes a page-invariant digest of the complete unreferenced
physical set and an exact deletion-free mark digest binding that set to folder,
operation, evidence, pin, visible-state, and payload-snapshot authority. Both
are non-durable diagnostics. All reclaim, policy, grace, writer-fenced
collection, quarantine-for-GC, and unlink authority remains false or absent.

## Adjacent cloudtainer correction

The first worktree acquired an unrelated partially wired payload-usage change
outside the reviewed patch. A fresh build exposed the mismatch. That worktree,
its build products, and all its validation output were rejected. Rev0975 was
reconstructed from the exact sealed rev0974 ZIP. The sealed payload-store
sources remained byte-identical, and the final binary-aware patch reconstructs
all 11 changed active files plus the complete 570-file active projection.

## Evidence summary

- Fresh GCC graph: 528/528 edges.
- Complete GCC registry: 258/258 tests.
- Independent GCC product replay: 39/39 tests.
- Structural audit: 312/312 checks.
- Fresh Clang ASan/UBSan product graph: 239/239 edges.
- Clang product lane: 39/39 tests with leak detection and halt-on-error.
- Focused sanitizer owner: 441 checks; local status: 155 checks.
- Exact rev0974 parent: SHA-256 matched; 41/41 package checks.
- Diagnostic scan: no retained compiler, linker, ASan, UBSan, runtime-error,
  or LeakSanitizer diagnostic.

See `PAGE_INVARIANT_DELETION_FREE_MARK_WITNESS_AUDIT_rev0975.md` for the full
implementation boundary and the future durable collector protocol.
