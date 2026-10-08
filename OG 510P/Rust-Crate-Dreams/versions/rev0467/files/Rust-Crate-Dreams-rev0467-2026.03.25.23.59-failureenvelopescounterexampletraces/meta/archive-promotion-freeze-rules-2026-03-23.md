# Archive promotion and freeze rules — 2026-03-23

## Why this note exists

The repo now contains enough packet vocabulary that future passes could easily make it worse by:
- silently overwriting old decisions,
- flattening compare/refresh/transition into one blob,
- or promoting crates before they have a credible receiver-facing packet.

This note is a guardrail for later passes, especially LLM-assisted ones.

## Promotion rule

Do **not** promote a proposal into the practical core unless it can name:
- one receiver cohort,
- one repeated workflow,
- one packet family,
- one basis story,
- one refresh or drift story,
- and one refusal boundary.

If any one of those is missing, it may still be important, but it is not ready for practical-core promotion.

## Freeze rule

When the repo has already frozen a decision, later passes should:
- append a new refresh/revalidation note,
- point back to the older basis,
- and explain whether the old answer still stands.

They should **not** silently rewrite the old answer as if it was always the new one.

## Rerank rule

Do **not** rerank the frontier unless the pass can state one concrete practical consequence such as:
- a new top-slice pairing,
- a crate moving into or out of the practical queue,
- or a new ranking criterion that future passes should remember.

If the pass cannot state a concrete practical consequence, prefer a narrower product-plan or fixture pass instead.

## Breadth rule

Do **not** create a new sector lane merely because a use case is real.
First test whether the use case can be absorbed by an existing control-plane crate through:
- a scenario pack,
- a receiver variation,
- a packet-family extension,
- or a basis/refresh rule.

Only open a new lane when there is a genuine evidence seam the current frontier cannot absorb.

## Freshness rule

When a pass uses current ecosystem signals, it should record:
- what changed recently,
- which facts are imported versus inferred,
- and what review horizon or freshness window the pass assumed.

## Minimal file discipline per refresh

A good incremental pass should usually add:
- one entry,
- one frontier note,
- one product-plan or theory note,
- and at least one schema or scenario fixture.

That keeps the archive from becoming essay-heavy and artifact-light.

## What this provides other people

This meta layer provides:
- less archive amnesia,
- fewer silent rewrites,
- a clearer standard for promotion,
- and a better chance that future LLM passes extend the repo instead of smearing it.
