# ChatGPT proof evaluator check registry

Rev0324 refactors the ChatGPT first-proof evaluator so the payload-level verdict cannot silently drift away from the canonical required-check list.

## Problem audited

Before rev0324, the evaluator had two sources of truth:

1. `REQUIRED_CHECKS`, which named the checks that must pass.
2. A manually duplicated payload-level merge dictionary, which copied most required checks out of attempt-level results.

That shape was fragile. A future schema gate could be added to `REQUIRED_CHECKS` and an individual attempt verdict, but accidentally omitted from the payload-level merge dictionary. The result would be confusing at best and unsafe at worst.

## Refactor

The evaluator now partitions checks into:

```text
ATTEMPT_SCOPED_CHECKS = REQUIRED_CHECKS - GLOBAL_ONLY_CHECKS
GLOBAL_ONLY_CHECKS = single_coherent_attempt_has_required_evidence, no_cross_surface_conflicts
```

`merge_required_checks(...)` iterates over `REQUIRED_CHECKS` directly. Attempt-scoped checks are merged from attempt verdicts. Global-only checks are computed once from the whole payload.

## Self-audit

Every evaluation now emits `check_registry_audit` with:

```text
required_check_count
attempt_scoped_check_count
global_only_check_count
duplicates
unknown_global_only_checks
missing_from_partition
extra_in_partition
overlap_between_global_and_attempt_scoped
```

A false `check_registry_audit.ok` is an implementation blocker. Do not use the evaluator verdict for proof review until the registry is repaired.

## Bundle-audit command

`python scripts/chatgpt-first-proof-bundle-audit.py audit ...` renders the evidence graph before evaluator review. It summarizes:

```text
action nodes
sequence edges
attempt counts
action types in sequence order
missing sequence indices
duplicate sequence indices
tab ids
conversation route paths
evaluator summary
check registry audit
```

The bundle audit is diagnostic only. It never widens support claims, never marks a surface public-citable, and never replaces the semantic evaluator or human privacy/redaction review.
