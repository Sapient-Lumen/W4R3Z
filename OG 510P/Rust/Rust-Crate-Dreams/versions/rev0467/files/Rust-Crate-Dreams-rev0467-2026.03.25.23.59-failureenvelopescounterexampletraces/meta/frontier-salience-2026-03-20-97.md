# Frontier salience snapshot — 2026-03-20 (97)

This pass did **not** add another release bot, another changelog normalizer, or a generic docs-navigation subsystem.
It deepened **P-0514 Crate Upgrade Pack Kit** by making one more receiver-facing truth explicit:

- **public-trace-path truth** — exported summary claims can now say which public route a reader should actually follow, whether that route resolves, and which typed miss kind applies when it does not.

## Main judgment

The sharper missing layer is still the joined upgrade-support contract above Cargo and ecosystem substrate.
But after source lineage, readiness, export posture, warnings, freshness, summary traceability, capture context, and sparse coverage became explicit, the next ordinary lie sat on the public route itself:

1. a public summary claim could still sound inspectable while its promised evidence route was private or broken,
2. and a fragment/target miss could still lose the fact that the **public trace path** failed.

Those are not tiny docs nits.
They are ordinary ways a polished public contract can overstate what downstream readers can actually inspect.

## Why this beat nearby work again

The archive already had enough to say:

- what the hazards were,
- where they came from,
- whether the pack was ready, exportable, current, and traceable,
- and which public files were exported.

What it still lacked was one compact way to say:

- “this public claim lands here,”
- “this warning-bearing claim lands here instead,”
- and “this pack is not frozen-public yet because the promised public trace path still fails with a typed miss.”

That is a real product refinement, not just extra structure.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — stronger again because exported claims are now harder to overstate as publicly inspectable.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
