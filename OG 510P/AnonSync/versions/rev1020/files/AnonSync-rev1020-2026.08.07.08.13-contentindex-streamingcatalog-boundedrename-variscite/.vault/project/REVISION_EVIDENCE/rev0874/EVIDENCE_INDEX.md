# AnonSync rev0874 evidence index

## Authority records

- `ACTIVE_IMPLEMENTATION_PROJECTION.json`: exact v2 inventory, byte counts, and
  SHA-256 for every active implementation path.
- `CHANGESET.json`: active additions/removals/modifications and authority changes.
- `LINEAGE.json` / `LINEAGE.md`: verified parent, patch identity, and replay scope.
- `AUDIT.md`: mission, corrected defects, evidence, gaps, and recommended next
  vertical slice.
- `SOURCE_DIFF_rev0873_to_rev0874.patch`: source and handoff-document delta from
  the verified parent.

## Validation records

The `validation/` directory retains the full Debug CTest log and registry,
focused runtime logs, 20-iteration owner stress, separate machine-readable clock,
lease, and owner structural audits, Clang warning build/runtime logs, GCC
ASan/UBSan build/runtime logs, Clang analyzer scope/results, active parent delta,
source-patch replay evidence, and hygiene output.

## Parent lineage

The `lineage/` directory retains the exact parent archive hash and current
verifier reports for both the rev0873 ZIP and its extracted canonical directory.

## Scope and nonclaims

- `operational/SANITIZER_SCOPE.md` states exactly which boundaries were
  instrumented/analyzed and which broader claims are excluded.
- `RESEARCH.md` records primary sources and separates takeaways from speculation.
- `NEXT_WORK.md` prioritizes receiver effect ownership, authentication, complete
  retry policy, differential incremental ownership, clock trust, generated state
  testing, and resource/privacy models.
- `REPOSITORY_HYGIENE.md` explains staging exclusions and why final directory/ZIP
  verifier reports remain outside the immutable artifact.

`EVIDENCE_INDEX.json` hashes every other file in this revision evidence directory
and intentionally excludes itself.
