# Cargo tool-workflow stack — incubation note (2026-03-08)

Purpose: stop letting three adjacent Cargo/tooling ideas blur into one fuzzy “editor and tooling pain” bucket.

## The three adjacent proposals

- **P-0494 Cargo Compile-Time-Deps Workflow Kit**
- **P-0490 Cargo Lock Contention Witness Kit**
- **P-0489 Cargo Build-Dir Consumer Transition Kit**

These proposals are close enough that future passes should actively check whether a claimed new idea is really just another missing layer or fixture family inside this stack.

## What each crate provides other people

### P-0494 — Cargo Compile-Time-Deps Workflow Kit
Provides a **tool-surface / parity / fallback artifact**:
- what command actually ran,
- what compile surface it covered,
- what assumptions were in play,
- and when a full build is required.

Other people get:
- one editor/build parity receipt,
- one CI preflight or support artifact,
- and one conservative vocabulary for “acceptable tool surface” versus “full build required”.

### P-0490 — Cargo Lock Contention Witness Kit
Provides a **live wait / blocking artifact**:
- who was blocked,
- on which root,
- for how long,
- and what mitigation makes sense.

Other people get:
- one answer to “who is blocking this build?”
- one lock-wait bundle for support or CI,
- and one mitigation vocabulary for shared target dirs, cache roots, and wrapper mismatches.

### P-0489 — Cargo Build-Dir Consumer Transition Kit
Provides an **internal-layout dependency audit artifact**:
- which tools scrape Cargo internals,
- what path assumptions they rely on,
- what adapter is safer,
- and what breaks under layout transition.

Other people get:
- one transition receipt for Cargo upgrades,
- one audit of risky path scraping,
- and one path-contract layer that is more stable than folklore.

## Recommended incubation order

### First: P-0494
Why first:
- current Cargo and rust-analyzer docs make the workflow boundary unusually explicit,
- the receiver-facing artifact is easy to explain,
- and its vocabulary can be reused by the other two proposals.

### Second: P-0490
Why second:
- it is highly practical,
- but it benefits from reusing P-0494’s workflow-role and target-dir policy vocabulary,
- and it should stay focused on **waiting** rather than drifting into parity or correctness claims.

### Third: P-0489
Why third:
- it is strategically important,
- but more upstream-sensitive,
- and it benefits from already having clear vocabulary for tool roles, target-dir policy, and fallback zones.

## Shared contract vocabulary the stack should converge on

Across all three crates, keep these ideas aligned:

- `workflow_role`
- `target_dir_policy`
- `observed_fact`
- `conservative_inference`
- `manual_review_required`
- `redaction_policy`
- `comparison_baseline`
- `bundle_schema_version`

If future passes rename these independently in each proposal, that is drift.

## Anti-patterns for this stack

- Do not make **P-0494** pretend tool-facing workflows inherit `cargo build` guarantees.
- Do not make **P-0490** become another generic build profiler or scheduler.
- Do not make **P-0489** become another cache manager or another artifact-handoff kit.
- Do not collapse “waited on another process” into “rebuilt too much” or “tool-only workflow was misleading”; those are different failures.

## Repo implication

For the next few passes, the archive should prefer:
- fixture/schema stubs,
- explicit receiver-facing bundle definitions,
- and layer-boundary notes across P-0494 / P-0490 / P-0489,

rather than adding another loosely defined Cargo IDE/tooling proposal.
