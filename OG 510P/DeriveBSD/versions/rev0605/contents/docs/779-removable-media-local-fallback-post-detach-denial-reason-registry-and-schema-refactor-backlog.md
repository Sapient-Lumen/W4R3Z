# Removable-media local fallback post-detach denial reason registry and schema refactor backlog

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r523 made scenario replay inspectable through ordered transition witnesses. r524 adds the decision-selection layer beneath those witnesses and turns the cube schema audit into an actionable refactor backlog.

See also:

- ADR: `adrs/ADR-0368-removable-media-local-fallback-post-detach-denial-reason-registry-and-schema-refactor-backlog-are-typed.md`
- denial reason registry schema: `spec/removable.media.local.post_detach.denial.reason.registry.schema.json`
- denial reason registry example: `spec/examples/removable.media.local.post_detach.denial.reason.registry.json`
- denial reason registry red corpus: `spec/examples/invalid/removable-media/post-detach-denial-reason-registry/`
- denial reason registry checker: `tools/check_removable_media_local_post_detach_denial_reason_registry.py`
- schema refactor backlog schema: `spec/cube.schema.refactor.backlog.schema.json`
- schema refactor backlog example: `spec/examples/cube.schema.refactor.backlog.json`
- schema refactor backlog checker: `tools/check_cube_schema_refactor_backlog.py`
- current denial-reason view: `docs/current/removable-media-post-detach-denial-reason-registry.md`
- current schema-refactor view: `docs/current/cube-schema-refactor-backlog.md`

## Decision

The new r524 posture tokens are `denial-reason-registry-positive-and-negative-fixture-guarded` and `cube-schema-refactor-backlog-live-scan-guarded`.

The denial reason registry is not another denial receipt. It is the decision table that tells a broker which reason code and rank to use when r521-r523 evidence surfaces overlap. It binds the r521 state machine, r522 replay manifest, r523 transition witness, r521 enforcement ledger, fresh-authority recovery receipt, and the legacy r510 denial receipt by computed digest.

The schema refactor backlog is not a style report. It is a live inventory of const-heavy schemas that should be migrated through the r520 split pattern: generic runtime schema, exact fixture schema, and semantic checker. It keeps historical fixture surfaces visible without forcing old examples to masquerade as dynamic production outputs.

## Denial reason coverage

The registry defines ranked reason codes for:

1. `raw-support-visibility` as a highest-priority sanitization failure.
2. `tombstone-visible` as the legacy r510 stale-authority denial.
3. `expired-ledger-root-fresh-authority-required` as the r521 post-expiry compacted-root denial.
4. `stale-root` as rollback/fork/stale-root denial.
5. `missing-expiry-receipt` as fail-closed missing expiry proof.
6. `degraded-clock` as fail-closed degraded time proof.
7. `missing-fresh-authority` as subordinate context that must not preempt the primary reason.
8. `rate-limit-replayed-no-new-debit` as idempotent replay behavior.
9. `none-successor-authority` as the non-denial success state after fresh authority is consumed and a successor root is admitted.

`lower-rank-wins` is the precedence rule. Subordinate reason codes can explain context, but they cannot outrank the primary denial cause. Support visibility remains `support-safe-digest-only` for every reason, including sanitization failures.

## Schema refactor backlog

The backlog is regenerated from the live schema tree. It records every schema whose literal `const` count is above the live audit threshold, assigns a domain, priority, status, and recommended action, and then binds back to `cube.schema.audit.report` by computed digest.

The current priority rule is intentionally conservative:

- open post-detach const-heavy schemas are `p0` because they are on the active runtime lane;
- other high-count schemas remain visible but lower priority;
- the r520 exact fixture schema is marked `completed-production-fixture-split` rather than counted as an open migration.

This lets the cube keep append-only history while still steering future work away from new fixture-literal runtime contracts.

## Red corpus

The denial reason red corpus rejects:

- duplicate precedence ranks;
- stale source digest bindings;
- missing `expired-ledger-root-fresh-authority-required`;
- scenario reason-code drift;
- raw support visibility;
- subordinate reasons that preempt the primary denial reason.

## Hygiene

Run:

```text
python3 tools/check_removable_media_local_post_detach_denial_reason_registry.py
python3 tools/check_cube_schema_refactor_backlog.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/hygiene.py --profile post-detach
python3 tools/hygiene.py --profile schema-cube-audit
```

Run the generic schema and generated-doc checks after touching schemas, examples, or docs:

```text
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_generated_docs.py
```

Last updated: 2026-05-30r524
