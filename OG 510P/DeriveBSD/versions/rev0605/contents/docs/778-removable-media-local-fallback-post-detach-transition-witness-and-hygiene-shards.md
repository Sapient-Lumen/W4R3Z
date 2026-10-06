# Removable-media local fallback post-detach transition witness and hygiene shards

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r522 proved the important post-detach scenarios at the outcome level. r523 adds a witness layer beneath those scenarios and an audit/refactor layer around archive hygiene itself.

See also:

- ADR: `adrs/ADR-0367-removable-media-local-fallback-post-detach-transition-witness-and-hygiene-shards-are-typed.md`
- transition witness schema: `spec/removable.media.local.post_detach.transition.witness.capsule.schema.json`
- transition witness example: `spec/examples/removable.media.local.post_detach.transition.witness.capsule.json`
- transition witness red corpus: `spec/examples/invalid/removable-media/post-detach-transition-witness-capsule/`
- transition witness checker: `tools/check_removable_media_local_post_detach_transition_witness.py`
- hygiene checkset schema: `spec/cube.hygiene.checkset.manifest.schema.json`
- hygiene checkset example: `spec/examples/cube.hygiene.checkset.manifest.json`
- hygiene checkset checker: `tools/check_cube_hygiene_checkset_manifest.py`
- profiled hygiene wrapper: `tools/hygiene.py --profile release-critical`
- current witness view: `docs/current/removable-media-post-detach-transition-witness.md`
- current hygiene view: `docs/current/cube-hygiene-checkset.md`

## Decision

The new r523 posture tokens are `transition-witness-capsule-positive-and-negative-fixture-guarded` and `cube-hygiene-checkset-sharded-live-scan-guarded`.

The transition witness capsule is not a new authority receipt. It is an executable transcript over the r522 replay model. It records the ordered steps that got from the scenario's initial condition to its terminal state, including from/to state names, required receipt kinds, computed receipt digests, support visibility, rate-limit behavior, idempotency behavior, time posture, and a computed outcome digest for each trace.

The hygiene checkset manifest is not a replacement for full hygiene. It is a typed map of the full hygiene surface into bounded shards so humans and CI can reason about what was run: release-critical, post-detach, generated-surface, schema-cube-audit, deep-contract, or all.

## Transition witness coverage

The r523 witness capsule carries one trace for each r522 scenario:

1. `expired-root-denied-with-enforcement-ledger` includes the post-expiry observe attempt, expiry receipt load, enforcement-ledger commit, support projection, and backend evidence collection.
2. `missing-expiry-receipt-fails-closed` records a typed denial and support projection instead of guessing that the root is usable.
3. `rollback-or-stale-root-is-rejected` records stale-root detection before the enforcement-ledger outcome.
4. `degraded-time-proof-fails-closed` records degraded time as a fail-closed denial, not a warning.
5. `fresh-authority-recovers-to-successor-root-only` records fresh authority, one-time consumption, successor cutover, and successor-reader admission; it never makes the expired root observable.
6. `same-idempotency-key-replays-same-denial-without-double-debit` records denial replay with `replayed-no-new-debit` rather than a second rate-limit debit.

## Transition witness red corpus

The red corpus rejects:

- skipped enforcement-ledger commit;
- non-monotonic witness step order;
- stale/non-computed model binding digest;
- raw support/debug visibility;
- fresh-authority recovery that resurrects an expired root;
- idempotent retry that double-debits rate limits.

These failures are intentionally semantic. A JSON shape can look plausible while still being unsafe as a transition transcript.

## Hygiene shard refactor

`tools/hygiene.py` still defaults to the full checkset, but it now accepts:

```text
python3 tools/hygiene.py --profile release-critical
python3 tools/hygiene.py --profile post-detach
python3 tools/hygiene.py --profile generated-surface
python3 tools/hygiene.py --profile schema-cube-audit
python3 tools/hygiene.py --profile deep-contract
python3 tools/hygiene.py --profile all
```

`cube.hygiene.checkset.manifest` is regenerated from the live tool tree. It proves:

- every top-level top-level check guardrails guardrail is referenced by hygiene exactly once;
- every hygiene-referenced check exists;
- every check belongs to exactly one shard;
- the release-critical profile is bounded and not the same as the full wrapper;
- the post-detach, generated-surface, and schema-cube-audit profiles exist.

This turns the repeated full-wrapper timeout problem into a visible profile/run-policy problem instead of a hidden failure mode.

## Hygiene

Run:

```text
python3 tools/check_removable_media_local_post_detach_transition_witness.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/hygiene.py --profile release-critical
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

Last updated: 2026-05-30r523
