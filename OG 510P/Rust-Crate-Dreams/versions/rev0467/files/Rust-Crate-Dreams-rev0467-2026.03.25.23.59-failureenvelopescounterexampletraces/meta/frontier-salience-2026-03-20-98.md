# Frontier salience snapshot — 2026-03-20 (98)

This pass did **not** add another release bot, another scope dashboard, or a generic workspace manager.
It deepened **P-0514 Crate Upgrade Pack Kit** by making one more receiver-facing truth explicit:

- **lane-selection origin truth** — upgrade packs can now say what invocation subject, manifest walk, workspace attachment, and normalized package/feature/target selection actually produced the reviewed lane.

## Main judgment

The sharper missing layer is still the joined upgrade-support contract above Cargo and ecosystem substrate.
But after package-scope truth, capture-context truth, sparse coverage matrices, export posture, and public trace routes became explicit, the next ordinary lie sat underneath scope itself:

1. a workspace-root run could still sound like explicit maintainer scoping when Cargo ambient `default-members` were the real cause,
2. and a skipped/gated target could still sound reviewed-clean instead of merely outside the selected lane.

Those are not tiny repo-shape details.
They are ordinary ways a polished migration contract can overstate how deliberate its reviewed scope really was.

## Why this beat nearby work again

The archive already had enough to say:

- which packages and cells were covered,
- which imports and summaries were exact,
- and which public claims a downstream reader could inspect.

What it still lacked was one compact way to say:

- “this lane came from workspace-root `default-members`, not explicit maintainer exclusion,”
- “this wider lane came from explicit `-p` selection overriding ambient defaults,”
- and “this target is absent because `required-features` kept it out of the lane, not because it was observed and passed.”

That is a real product refinement, not just extra structure.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — stronger again because reviewed scope is now harder to overstate as deliberate when Cargo defaults shaped it.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
