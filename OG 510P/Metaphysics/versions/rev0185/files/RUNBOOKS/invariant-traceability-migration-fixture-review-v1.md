# Invariant, Traceability, Migration, and Fixture Review Runbook v1

## Purpose

Use this runbook when a release adds, removes, renames, migrates, deprecates, or materially changes a governance artifact, current record family, query, validator, schema, control-stack step, or public-claim boundary.

## Required stages

1. Identify new or changed control surfaces.
2. Add or update invariants in `INVARIANT_CATALOG.yml`.
3. Add or update requirement rows in `TRACEABILITY_MATRIX.yml`.
4. Add or update change-impact rows in `CHANGE_IMPACT_MATRIX.yml`.
5. Add or update migration/deprecation entries in `MIGRATION_LEDGER.yml`.
6. Add positive or negative fixtures in `FIXTURE_CORPUS.yml` when the validator would otherwise have only a happy-path test.
7. Update `STATUS_VOCABULARY.yml` before any new status token appears in a current record.
8. Update `CUBE_INDEX.yml`, `CONTROL_STACK.yml`, `QUERY_REGRESSION_SUITE.yml`, current records, reports, front doors, and manifest.
9. Run local validation, query regression, invariant check, traceability check, reference check, and fixture runner.
10. Preserve the local-only warning in summaries and handoffs.

## Stop conditions

Stop release if a current record misses required fields, a current status token is undefined, a required local reference is missing, a control-stack successor is broken, a cube source artifact is missing, query regression fails, a critical traceability requirement is uncovered, fixture corpus lacks negative pressure, or manifest integrity fails.

## Forbidden claims

This runbook does not establish public CI, public issue tracking, formal verification, semantic theorem proving, external QA, source freshness, domain review, safety-case sufficiency, or operational deployment readiness.
