# Cargo Build-Dir Consumer Transition — dual-support refinement plan (2026-03-23)

This note deepens **P-0489 Cargo Build-Dir Consumer Transition Kit**.
The proposal and product plan already established the migration-first frame.
This pass sharpens the operational center:

> What should the crate provide other people during the real legacy-layout to new-layout transition window, especially when the right answer is not “flip now”, but “support both layouts honestly for a while”?

## Main judgment

`0.1` should treat **dual-support planning** as first-class.
The crate should not merely say “this consumer is scraping Cargo internals”.
It should say whether the next honest move is:

- `migrate_now`
- `support_both_layouts`
- `hold_current_and_rehearse`
- `blocked_on_upstream`
- or `manual_review_required`

That is what maintainers actually need during Cargo layout change rehearsals.

## Why now

Cargo’s March 2026 testing call for Build Dir Layout v2 made three things unusually explicit:

1. many tools still rely on unspecified layout details,
2. Cargo wants users to rehearse their tests and release flows against the new layout,
3. some replacement advice is **windowed** by Cargo version or workflow shape.

That turns this proposal from generic migration tooling into a live ecosystem need.

## What the crate should provide other people

### For workspace maintainers
- one inventory of build-dir consumers,
- one explanation of the real consumer need,
- one authority receipt for the suggested adapter,
- one viability matrix across legacy/new layout and Cargo-version windows,
- one explicit recommendation about whether dual support is required.

### For tool authors
- one narrow statement of which assumptions are fragile,
- one path-contract or handoff alternative when it exists,
- one honest “blocked on upstream” output when it does not.

### For release / CI operators
- one rehearsal bundle that compares current vs new layout outcomes,
- one diff that says whether risk went up, stayed bounded, or moved to a new consumer family.

## The operational model

### Classify the consumer need first
Before suggesting any adapter, the crate must classify what the consumer was actually trying to do.

Initial need classes:
- `integration_test_binary`
- `build_script_owned_output`
- `final_artifact`
- `dep_info`
- `workspace_topology_guess`
- `intermediate_compiler_artifact`
- `manual_review_required`

This matters because the right replacement depends on the real need.

### Then classify adapter authority
Suggested adapter routes are only trustworthy if the justification source is visible.

Initial authority classes:
- `cargo_docs_stable`
- `cargo_release_notes`
- `cargo_testing_guidance`
- `cargo_unstable_docs`
- `project_goal_context`
- `issue_thread_workaround`
- `local_heuristic_only`

### Then classify windowed viability
An adapter can be good in principle but only usable in some windows.

Initial viability dimensions:
- legacy layout
- custom `build.build-dir`
- `-Zbuild-dir-new-layout`
- minimum Cargo version
- nightly requirement
- fallback requirement
- local-only heuristic remainder

### Then decide the operational recommendation
Initial recommendation classes:
- `migrate_now`
- `support_both_layouts`
- `hold_current_and_rehearse`
- `blocked_on_upstream`
- `manual_review_required`

## Recommended new `0.1` artifacts

Keep the earlier inventory / need / path / adapter core.
Add two more first-class artifacts:

### `dual-support.plan.json`
Purpose:
- say whether the workflow needs legacy/new-layout support at the same time,
- record why,
- record the planned retirement trigger.

Suggested fields:
- `consumer_id`
- `recommendation`
- `legacy_support_required`
- `new_layout_support_required`
- `minimum_modern_cargo`
- `fallback_strategy`
- `retirement_trigger`
- `notes`

### `windowed-migration.receipt.json`
Purpose:
- join consumer need, adapter authority, viability matrix, and dual-support plan for one rehearsal outcome.

Suggested fields:
- `consumer_id`
- `cargo_version_window`
- `layout_mode`
- `adapter_route`
- `recommendation`
- `residual_risk`
- `manual_review_required`

## Adapter guidance that should be modeled explicitly

### `CARGO_BIN_EXE_*`
Strong when the need is integration-test binary lookup.
Weak when the consumer is really asking for arbitrary internal artifacts.

### `OUT_DIR`
Strong when the consumer owns build-script-generated outputs.
Weak when the workflow is actually trying to rediscover workspace topology.

### final-artifact handoff
Strong when the need is a produced binary/library for downstream tooling.
Weak when the workflow depends on compiler/intermediate internals.

### keep-scraping-temporarily
Sometimes the honest `0.1` answer is “still scraping, because no adequate supported surface exists yet”.
That should be visible, not hidden.

## Proving grounds for `0.1`

1. test code infers a binary path from test-path topology and should migrate to `CARGO_BIN_EXE_*`.
2. a helper walks `target/.../build/...` but really wants build-script-owned output.
3. a release script wants the final produced artifact, not intermediate state.
4. a tool inspects dep-info and has a real documented route.
5. a tool wants intermediate compiler artifacts and remains partially blocked.
6. one consumer can migrate now while another consumer in the same workspace needs dual support.
7. one migration route is only valid above a Cargo floor and therefore needs a fallback lane.

## Important design boundaries

### “Adapter exists” is not enough
The crate must say whether the adapter fits the consumer need and window.

### “Nightly rehearsal works” is not the same as “stable migration complete”
Keep those separate.

### “Still scraping” can be the honest output
Do not hide unresolved upstream gaps.

### “Dual support” is not failure
In transition windows it is often the correct operational answer.

## What should wait until later

- automatic patching or codemods for every consumer family,
- a fake universal path API over Cargo internals,
- ambitious IDE/editor integrations before the bundle model is stable,
- and global migration orchestration.

The first win is a crisp rehearsal bundle and a truthful dual-support plan.
