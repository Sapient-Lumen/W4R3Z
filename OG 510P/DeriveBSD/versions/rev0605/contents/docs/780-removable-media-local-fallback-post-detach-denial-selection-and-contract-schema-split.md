# Removable-media local fallback post-detach denial selection and contract schema split

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r524 made denial reason precedence typed. r525 adds the per-attempt selection receipt that proves the registry was actually used, and it performs the first backlog-driven split of the oldest const-heavy post-detach contract schema.

See also:

- ADR: `adrs/ADR-0369-removable-media-local-fallback-post-detach-denial-selection-and-contract-schema-split-are-typed.md`
- denial selection schema: `spec/removable.media.local.post_detach.denial.selection.receipt.schema.json`
- denial selection example: `spec/examples/removable.media.local.post_detach.denial.selection.receipt.json`
- denial selection red corpus: `spec/examples/invalid/removable-media/post-detach-denial-selection-receipt/`
- denial selection checker: `tools/check_removable_media_local_post_detach_denial_selection_receipt.py`
- runtime contract schema: `spec/removable.media.local.post_detach.contract.schema.json`
- exact contract fixture schema: `spec/removable.media.local.post_detach.contract.fixture.schema.json`
- current denial-selection view: `docs/current/removable-media-post-detach-denial-selection.md`
- current schema-refactor view: `docs/current/cube-schema-refactor-backlog.md`

## Decision

The new r525 posture tokens are `denial-selection-receipt-positive-and-negative-fixture-guarded` and `post-detach-contract-generic-runtime-schema-plus-exact-fixture-split`.

The denial selection receipt is the execution bridge between the r524 registry and an individual broker attempt. It records the active/inactive predicates, candidate denial reasons, selected reason, subordinate reason codes, support projection, scenario/witness binding, and rate-limit behavior.

The contract schema split is the first concrete migration from the r524 backlog. The original exact r504 contract shape is preserved under `spec/removable.media.local.post_detach.contract.fixture.schema.json`; the production schema keeps closed-world safety fields but moves dynamic ids and digests into a runtime-shaped `$defs`/pattern contract.

## Denial selection coverage

The r525 positive receipt covers the `expired-root-denied-with-enforcement-ledger` scenario. It proves that:

- `raw-support-visibility` and `tombstone-visible` were not active;
- `expired-ledger-root-fresh-authority-required`, `stale-root`, and `missing-fresh-authority` were active;
- `expired-ledger-root-fresh-authority-required` won because `lower-rank-wins` selects rank 20 over rank 30 and rank 70;
- `missing-fresh-authority` remains subordinate context;
- observe/export/rehydrate remain denied;
- the rate-limit action is `debit` with one debit;
- the support projection remains `support-safe-digest-only`.

## Red corpus

The denial selection red corpus rejects:

- stale denial-reason registry digest bindings;
- active higher-precedence causes that are omitted from selection;
- unknown selected reason codes;
- subordinate reasons selected as primary causes;
- raw support/debug visibility;
- rate-limit action drift;
- witness/scenario binding drift.

## Schema refactor result

The live schema audit now reports the contract runtime schema as runtime-shaped and records the exact historical contract fixture separately. The const-heavy count remains intentionally visible because fixture schemas still carry history, but the open backlog shrinks: the post-detach contract split is complete and the next p0 targets remain visible.

## Hygiene

Run:

```text
python3 tools/check_removable_media_local_post_detach_denial_selection_receipt.py
python3 tools/check_removable_media_local_post_detach_denial_reason_registry.py
python3 tools/check_removable_media_local_post_detach_contract_closure.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/check_cube_schema_refactor_backlog.py
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

Last updated: 2026-05-30r525
