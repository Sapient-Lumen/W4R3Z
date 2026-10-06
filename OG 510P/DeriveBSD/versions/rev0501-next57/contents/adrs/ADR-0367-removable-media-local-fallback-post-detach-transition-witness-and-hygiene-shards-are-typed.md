# ADR-0367: Removable-media local fallback post-detach transition witness and hygiene shards are typed

## Status

Accepted.

## Context

r521 made the removable-media local fallback post-detach lane runtime-verifiable at the artifact level. r522 replayed the important end-to-end scenarios. That still left two problems.

First, the replay manifest described scenarios, but did not carry a step-by-step witness transcript that a reviewer could audit without re-deriving the transition sequence. A scenario could have the correct terminal outcome while hiding a skipped enforcement-ledger step, a raw support projection, a resurrection of an expired root during recovery, or a double rate-limit debit during idempotent replay.

Second, the archive's hygiene wrapper had become a flat, large all-check list. It still mattered as a full CI-style surface, but it repeatedly exceeded short interactive release windows. The cube needed a typed shard manifest and a profiled wrapper so release-critical, post-detach, generated-surface, schema-audit, and deep-contract checks could be run deliberately without losing the all-check inventory.

## Decision

Add a typed r523 transition-witness and hygiene-shard cut.

This cut adds:

- `spec/removable.media.local.post_detach.transition.witness.capsule.schema.json` and `spec/examples/removable.media.local.post_detach.transition.witness.capsule.json` as the ordered transition transcript for the r522 replay scenarios;
- `spec/examples/invalid/removable-media/post-detach-transition-witness-capsule/` as the red corpus for witness regressions: skipped enforcement ledger, non-monotonic steps, stale model binding, raw support visibility, expired-root resurrection, and idempotent retry double debit;
- `tools/check_removable_media_local_post_detach_transition_witness.py` as the semantic witness checker;
- `spec/cube.hygiene.checkset.manifest.schema.json` and `spec/examples/cube.hygiene.checkset.manifest.json` as the live shard manifest for `tools/hygiene.py`;
- `tools/check_cube_hygiene_checkset_manifest.py` as the checker that regenerates the live hygiene manifest, proves every check is referenced exactly once, and proves every check belongs to exactly one shard;
- a refactor of `tools/hygiene.py` to support `--profile release-critical`, `--profile post-detach`, `--profile generated-surface`, `--profile schema-cube-audit`, `--profile deep-contract`, and the original default `--profile all` behavior;
- current-view docs for the transition witness and hygiene checkset.

The new posture tokens are `transition-witness-capsule-positive-and-negative-fixture-guarded` and `cube-hygiene-checkset-sharded-live-scan-guarded`.

## Consequences

- Scenario replay now has a reviewable witness transcript with ordered steps, known from/to states, required receipt kinds, computed receipt digests, support-visibility posture, rate-limit behavior, idempotency behavior, and computed outcome digests.
- A recovery success can only be represented as successor-root admission. The expired root remains non-observable in the witness.
- Idempotent denial replay is explicitly represented as replayed with no new rate-limit debit.
- The r523 checker rejects witness files that are syntactically plausible but semantically unsafe.
- The all-check hygiene wrapper remains available, but release work can run bounded typed shards rather than treating a long timeout as the only validation surface.
- The hygiene manifest becomes an audit/refactor surface: it exposes how much of the cube is release-critical, post-detach focused, generated-surface, schema-audit, or deep-contract legacy.

## Validation

Run:

```text
python3 tools/check_removable_media_local_post_detach_transition_witness.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/hygiene.py --profile release-critical
python3 tools/hygiene.py --profile post-detach
python3 tools/hygiene.py --profile schema-cube-audit
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_version.py
```

`tools/check_removable_media_local_post_detach_transition_witness.py` validates the positive capsule, recomputes model bindings and outcome digests, checks trace/scenario parity, checks known state names, and proves the red corpus fails schema or semantic validation.

`tools/check_cube_hygiene_checkset_manifest.py` rebuilds the live hygiene-shard manifest from `tools/hygiene.py` and top-level top-level check guardrails scripts, then requires the checked-in manifest to match exactly.

Last updated: 2026-05-30r523
