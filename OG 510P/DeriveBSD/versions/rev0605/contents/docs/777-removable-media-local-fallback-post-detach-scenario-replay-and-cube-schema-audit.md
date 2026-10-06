# Removable-media local fallback post-detach scenario replay and cube schema audit

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r521 made the post-detach removable-media lifecycle runtime-verifiable at the artifact level. r522 adds the next verification layer: replay the important lifecycle scenarios end to end, and audit the cube's schema posture so the runtime-contract refactor backlog is no longer implicit.

See also:

- ADR: `adrs/ADR-0366-removable-media-local-fallback-post-detach-scenario-replay-and-cube-schema-audit-are-typed.md`
- scenario replay schema: `spec/removable.media.local.post_detach.scenario.replay.manifest.schema.json`
- scenario replay example: `spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json`
- scenario replay red corpus: `spec/examples/invalid/removable-media/post-detach-scenario-replay-manifest/`
- schema audit report schema: `spec/cube.schema.audit.report.schema.json`
- schema audit report example: `spec/examples/cube.schema.audit.report.json`
- canonical digest helper: `tools/cube_digest_lib.py`
- scenario checker: `tools/check_removable_media_local_post_detach_scenario_replay.py`
- schema audit checker: `tools/check_cube_schema_audit_report.py`
- current replay view: `docs/current/removable-media-post-detach-scenario-replay.md`
- current schema audit view: `docs/current/cube-schema-audit.md`

## Decision

The new r522 posture tokens are `post-detach-scenario-replay-positive-and-negative-fixture-guarded` and `cube-schema-audit-report-live-scan-guarded`.

The post-detach replay manifest is not another receipt in the authority chain. It is an executable review surface over the r521 chain. It binds to the computed digests of the r521 state-machine manifest, enforcement ledger receipt, fresh-authority recovery receipt, support projection, and backend evidence. Its job is to say what the whole lane does in representative situations.

## Replay scenarios

The replay manifest includes six scenarios:

1. `expired-root-denied-with-enforcement-ledger`: an observed post-expiry attempt loads the expiry receipt, commits the enforcement ledger, emits support-safe projection evidence, and collects backend evidence. Observation, export, and rehydration stay denied.
2. `missing-expiry-receipt-fails-closed`: if the broker cannot prove the root reached the expiry state, it does not guess or allow observation. It emits a typed fail-closed denial.
3. `rollback-or-stale-root-is-rejected`: stale, rollback, or forked roots cannot export or rehydrate by racing the enforcement ledger.
4. `degraded-time-proof-fails-closed`: an untrusted or degraded time proof is not a warning-only condition; it is a typed denial path.
5. `fresh-authority-recovers-to-successor-root-only`: fresh authority can recover the workflow only by consuming authority once and admitting a successor root. The expired root remains terminal.
6. `same-idempotency-key-replays-same-denial-without-double-debit`: replaying the same post-expiry attempt must return the same denial without creating a second rate-limit debit.

## Red corpus

The replay red corpus rejects:

- expired-root observation after expiry;
- missing-expiry proof that does not fail closed;
- stale-root export;
- degraded-time success;
- recovery that resurrects the expired root;
- idempotent replay double-debit;
- symbolic/non-computed model binding digests.

These are deliberately semantic failures. Some remain JSON-valid because the shape can be syntactically correct while the behavior is unsafe.

## Cube schema audit

The new `cube.schema.audit.report` is a deterministic live scan, not a hand-written inventory. It reports:

- total schemas and top-level examples;
- root-kind schema count;
- schemas with and without canonical examples;
- const-heavy schemas above the r522 threshold;
- runtime-contract-shaped schemas;
- exact fixture schemas;
- dotted-kind filename mismatches;
- the next post-detach schema-split targets.

The audit does not fail merely because old fixture-literal schemas exist. It fails if the checked-in report no longer matches the live cube, or if dotted-kind filename discipline regresses.

## Refactor

`tools/cube_digest_lib.py` centralizes the canonical JSON digest rule used by r521+ computed joins: sorted keys, compact separators, UTF-8, SHA-256. The r521 runtime state-machine checker and r522 replay/audit checkers use that helper so future computed joins have one serialization posture.

## Hygiene

Run:

```text
python3 tools/check_removable_media_local_post_detach_runtime_state_machine.py
python3 tools/check_removable_media_local_post_detach_scenario_replay.py
python3 tools/check_cube_schema_audit_report.py
```

Run the generic schema and generated-doc checks after touching schemas, examples, or docs:

```text
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_generated_docs.py
```

Last updated: 2026-05-30r522
