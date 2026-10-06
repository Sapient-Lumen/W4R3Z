# ADR-0368: Removable-media local fallback post-detach denial reason registry and schema refactor backlog are typed

## Status

Accepted.

## Context

r521 made the removable-media local fallback post-detach lane runtime-verifiable at the artifact level. r522 added end-to-end scenario replay. r523 added transition witnesses and made hygiene shardable. The remaining gap was cause selection: denial reason codes existed in the r510 tombstone denial receipt, r521 post-expiry enforcement ledger, r522 scenario replay, and r523 transition witness, but there was no single registry that defined which reason wins when several unsafe conditions are true at once.

The cube-wide schema audit also became useful enough to need an action surface. r522 and r523 counted const-heavy schemas, but a reviewer still had to infer which legacy fixture-heavy surfaces should be split next and which completed split should remain historical fixture evidence rather than unfinished work.

## Decision

Add a typed r524 denial-reason and schema-refactor cut.

This cut adds:

- `spec/removable.media.local.post_detach.denial.reason.registry.schema.json` and `spec/examples/removable.media.local.post_detach.denial.reason.registry.json` as the reason-code and precedence registry for post-detach denials and successor recovery;
- `spec/examples/invalid/removable-media/post-detach-denial-reason-registry/` as the red corpus for duplicate ranks, stale source bindings, missing primary expiry codes, scenario drift, raw support visibility, and subordinate reasons that preempt the primary denial;
- `tools/check_removable_media_local_post_detach_denial_reason_registry.py` as the semantic checker that recomputes source bindings, reads r522 scenarios and r523 witnesses, checks the r521 enforcement ledger and fresh-authority recovery, and proves the red corpus fails;
- `spec/cube.schema.refactor.backlog.schema.json` and `spec/examples/cube.schema.refactor.backlog.json` as a live backlog over every const-heavy schema in the cube;
- `tools/check_cube_schema_refactor_backlog.py` as the checker that regenerates the backlog from the live schema tree and the live cube schema audit;
- current-view docs for both surfaces.

The new posture tokens are `denial-reason-registry-positive-and-negative-fixture-guarded` and `cube-schema-refactor-backlog-live-scan-guarded`.

## Consequences

- Expired-root, tombstone, stale-root, missing-expiry, degraded-clock, idempotent replay, raw-support, and successor-success outcomes now have one typed place to define rank, class, rate-limit action, support visibility, and subordinate reason behavior.
- Lower numeric rank wins. Subordinate reasons may explain context, but they cannot preempt the primary denial reason.
- Successor recovery remains explicitly non-denial: `none-successor-authority` is allowed only when fresh authority has been consumed and the expired root remains non-observable.
- Support/debug surfaces after denial remain `support-safe-digest-only` regardless of the winning reason.
- The schema audit now has a paired backlog. Every live const-heavy schema is accounted for, the post-detach runtime lane is prioritized first, and the r520 production/fixture split is marked completed without rewriting old history.

## Validation

Run:

```text
python3 tools/check_removable_media_local_post_detach_denial_reason_registry.py
python3 tools/check_cube_schema_refactor_backlog.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/hygiene.py --profile post-detach
python3 tools/hygiene.py --profile schema-cube-audit
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_version.py
```

`tools/check_removable_media_local_post_detach_denial_reason_registry.py` validates the positive registry, recomputes source digests, checks scenario and witness parity, checks the r521 denial reason rank, and proves the red corpus fails.

`tools/check_cube_schema_refactor_backlog.py` validates the live backlog against the current schema tree and `cube.schema.audit.report`, so schema-count drift becomes a release-visible refactor decision rather than a hidden follow-up.

Last updated: 2026-05-30r524
