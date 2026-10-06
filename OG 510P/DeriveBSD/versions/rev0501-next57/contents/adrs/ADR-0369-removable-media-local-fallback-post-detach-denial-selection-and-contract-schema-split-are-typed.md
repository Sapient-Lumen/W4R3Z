# ADR-0369: Removable-media local fallback post-detach denial selection and contract schema split are typed

## Status

Accepted.

## Context

r524 gave the post-detach lane a single denial reason registry, but it still left an implementation gap between the registry and an individual broker attempt. A reviewer could see the ranked table and the scenario replay, but not a typed per-attempt receipt proving which predicates were active, which candidate reasons were considered, which reason won, which subordinate reasons were attached, and whether rate-limit and support projection behavior matched the winning cause.

The cube-wide schema backlog also named the oldest post-detach contract schema as the first const-heavy migration target. Keeping that schema as a literal fixture contract makes historical review easy, but it is a poor shape for runtime validation because dynamic broker ids and digests should validate without cloning one exact r504 example.

## Decision

Add a typed r525 denial-selection and schema-split cut.

This cut adds:

- `spec/removable.media.local.post_detach.denial.selection.receipt.schema.json` and `spec/examples/removable.media.local.post_detach.denial.selection.receipt.json` as the per-attempt denial selection receipt for the r524 registry;
- `spec/examples/invalid/removable-media/post-detach-denial-selection-receipt/` as the red corpus for stale registry bindings, omitted higher-precedence candidates, unknown selected reasons, subordinate selected reasons, raw support visibility, rate-limit action drift, and witness/scenario drift;
- `tools/check_removable_media_local_post_detach_denial_selection_receipt.py` as the semantic checker that recomputes source digests, reads the r524 registry, checks r522/r523 scenario and witness bindings, and proves the red corpus fails;
- `spec/removable.media.local.post_detach.contract.fixture.schema.json` as the exact historical r504 fixture schema for the post-detach contract;
- a rewritten `spec/removable.media.local.post_detach.contract.schema.json` as the runtime contract schema, preserving the closed-world safety envelope while allowing dynamic ids and digests through patterns and `$defs`;
- refreshed audit and backlog reports showing the contract split as completed while keeping the exact fixture schema visible as historical evidence.

The new posture tokens are `denial-selection-receipt-positive-and-negative-fixture-guarded` and `post-detach-contract-generic-runtime-schema-plus-exact-fixture-split`.

## Consequences

- Denial cause selection is no longer only implied by the registry. A single broker attempt now carries observed predicates, active candidates, selected reason, subordinate reason codes, allowed actions, support projection posture, and rate-limit behavior.
- The selected reason must be an active registry member and must be the lowest-rank active non-subordinate candidate. Subordinate reasons can be attached, but they cannot win.
- Support visibility remains `support-safe-digest-only`; any raw support visibility becomes a higher-priority sanitization failure.
- The r504 contract example remains exact under the fixture schema, while production validation moves to a generic runtime-shaped schema.
- The schema refactor backlog now records two completed production/fixture splits: the r520 expiry-enforcement receipt and the r504 post-detach contract.

## Validation

Run:

```text
python3 tools/check_removable_media_local_post_detach_denial_selection_receipt.py
python3 tools/check_removable_media_local_post_detach_denial_reason_registry.py
python3 tools/check_removable_media_local_post_detach_contract_closure.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/check_cube_schema_refactor_backlog.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_version.py
```

`tools/check_removable_media_local_post_detach_denial_selection_receipt.py` validates the positive receipt, recomputes source digests, verifies lower-rank-wins against the r524 registry, checks the r522/r523 scenario/witness join, and rejects every red-corpus shape.

Last updated: 2026-05-30r525
