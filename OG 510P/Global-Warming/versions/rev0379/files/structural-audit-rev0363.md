# Structural audit rev0363

## Findings

- Root README was stale: it still identified the archive as rev0312 while manifests identified rev0362.
- The uploaded rev0362 validator failed on direct execution because it substring-matched `closure` and misclassified `rejected_closure_attempt` as an automatic closure.
- The rev0362 validation report mixed executed checks with pending/planned package checks, all under `pass` status.
- Exact duplicate content remains small relative to the whole archive but unnecessary.
- Large traceability matrices and old SQLite mirrors dominate uncompressed size and should be considered for historical-evidence-bag treatment.
- Source IDs are inflated by repeated registrations of the same canonical URLs; duplicate source IDs must be aliases, not corroboration.
- Synthetic fixture files with risky extensions are text markers, but their extensions create avoidable security/operator friction.

## Corrections made

- README updated to rev0363.
- Validator exact-match fix applied to rev0362 path and new rev0363 path.
- Validator sweep added.
- Waste, source-alias, and firebreak audits added.
- Manifest/schema pointers updated.

## Corrections deferred

- Full archive slimming and historical SQLite eviction.
- Fixture extension renaming or fixture-manifest policy.
- Replacement of all historical validation reports that marked pending/reserved checks as pass.
