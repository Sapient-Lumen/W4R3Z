# ADR-0366: Removable-media local fallback post-detach scenario replay and cube schema audit are typed

## Status

Accepted.

## Context

r521 made the removable-media local fallback post-detach lane runtime-verifiable at the artifact level: the state-machine manifest, post-expiry enforcement ledger, fresh-authority recovery receipt, support projection, backend evidence, and r520 production/fixture split all became typed and semantically checked. That still left two useful gaps.

First, the lane needed an executable replay view. Individual receipts could be valid while an implementer still mishandled a whole scenario: observing after expiry, failing open when the expiry receipt is missing, exporting through a stale root, treating degraded time as a warning, resurrecting the expired root after fresh authority, or double-debiting rate limits on an idempotent retry.

Second, the broader cube needed a live schema-shape audit. r521 deliberately avoided rewriting older fixture-literal schemas. That was correct for history preservation, but it left the refactor backlog implicit. The next cut should make that backlog visible and mechanically reproducible without blocking base/helper schemas that are intentionally example-less.

## Decision

Add a typed r522 replay/audit cut for the ordinary B/C removable-media local fallback and the cube schema surface.

This cut adds:

- `spec/removable.media.local.post_detach.scenario.replay.manifest.schema.json` and `spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json` as the end-to-end scenario model for the r521 post-detach state machine;
- `spec/examples/invalid/removable-media/post-detach-scenario-replay-manifest/` as the red corpus for replay regressions: expired-root observation, missing-expiry fail-open, stale-root export, degraded-time success, expired-root resurrection after recovery, idempotent retry double-debit, and symbolic/non-computed model bindings;
- `tools/check_removable_media_local_post_detach_scenario_replay.py` as the semantic replay checker;
- `tools/cube_digest_lib.py` as the shared canonical JSON digest helper for r521+ computed joins;
- `spec/cube.schema.audit.report.schema.json` and `spec/examples/cube.schema.audit.report.json` as the deterministic live scan of the schema surface;
- `tools/check_cube_schema_audit_report.py` as the audit/report freshness checker;
- `docs/current/removable-media-post-detach-scenario-replay.md` and `docs/current/cube-schema-audit.md` as current-view implementation/audit surfaces.

The new posture tokens are `post-detach-scenario-replay-positive-and-negative-fixture-guarded` and `cube-schema-audit-report-live-scan-guarded`.

## Consequences

- The post-detach lane is now checked as scenarios, not only as isolated receipt shapes.
- The expired-root path, missing-expiry path, rollback/stale path, degraded-time path, fresh-authority successor path, and idempotent replay path are all explicit.
- Replays using the same idempotency key must return the same denial without creating a second rate-limit debit.
- Fresh authority after expiry clears the denial only by admitting a successor root; it never makes the expired root observable again.
- Computed digest joins use one helper rule in `tools/cube_digest_lib.py`, reducing checker drift.
- The cube now carries a deterministic schema audit with counts for total schemas, examples, root-kind schemas, canonical examples, helper schemas without examples, const-heavy schemas, runtime-contract-shaped schemas, exact fixture schemas, and dotted-kind filename mismatches.
- Older const-heavy post-detach schemas remain historical, but the next split targets are now visible and mechanically refreshed by the audit checker.

## Validation

Run:

```text
python3 tools/check_removable_media_local_post_detach_runtime_state_machine.py
python3 tools/check_removable_media_local_post_detach_scenario_replay.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_version.py
```

`tools/check_removable_media_local_post_detach_scenario_replay.py` validates the replay manifest, recomputes model binding digests, checks every scenario outcome, and proves the red corpus fails by schema or semantic checks.

`tools/check_cube_schema_audit_report.py` rebuilds the live schema audit from schemas under spec/ and top-level examples under spec/examples/, then requires the checked-in report to match exactly.

Last updated: 2026-05-30r522
