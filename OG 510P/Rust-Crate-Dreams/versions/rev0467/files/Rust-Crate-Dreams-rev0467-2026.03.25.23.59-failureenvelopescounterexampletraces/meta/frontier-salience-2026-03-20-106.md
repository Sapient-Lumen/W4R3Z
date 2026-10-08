# Frontier salience snapshot — 2026-03-20 (106)

This pass did **not** add another warning family, another export gate, or another replay/state layer.
It deepened **P-0514 Crate Upgrade Pack Kit** by making one more receiver-facing truth explicit:

- **surface-authorship truth** — upgrade packs can now say whether a surfaced artifact is Cargo-native generated evidence, maintainer-authored guidance, reviewer-authored governance, archive-derived presentation, or mixed context, and which trust plane that surface belongs to.

## Main judgment

After source-lineage, summary-claim traceability, review provenance, session honesty, replay bridges, and baseline-state surfaces became explicit, one ordinary lie still remained:

1. a lane could still make well-cited artifacts look more interchangeable than they really are,
2. and exact evidence refs could still launder maintainer guidance or derived summaries into the aura of native tool output.

Those are not small documentation details.
They change what kind of contract the pack is honestly allowed to export.

## Why this beat nearby work again

The archive already had enough to say:

- where the bytes came from,
- how a reviewer could replay them,
- and which public routes and warnings stayed visible.

What it still lacked was one compact way to say:

- “this is Cargo-native output,”
- “this is maintainer-authored guidance,”
- “this is reviewer-authored governance,”
- or “this sentence is archive-derived presentation.”

That is a real product refinement, not another naming flourish.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — stronger again because exact citations can no longer quietly flatten different authorship/trust planes into one source of truth.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
