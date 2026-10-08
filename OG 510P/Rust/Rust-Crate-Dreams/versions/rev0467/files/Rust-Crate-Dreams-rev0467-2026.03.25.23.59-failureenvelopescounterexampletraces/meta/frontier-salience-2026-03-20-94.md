# Frontier salience snapshot — 2026-03-20 (94)

This pass did **not** add another dashboard or richer changelog summarizer.
It deepened **P-0514 Crate Upgrade Pack Kit** by making two more receiver-facing truths explicit:

- **revalidation-window truth** — every pack can declare its review clock, material-change triggers, and supersession rule;
- **freshness-state truth** — every pack can say whether it is still current, merely stale-but-usable, fully expired, or already superseded.

## Main judgment

The sharper missing layer is still the **joined upgrade-support contract** above today’s substrate.
But after authority, readiness, consistency, export, deviations, and warnings became explicit, the next ordinary lie sat in time itself:

1. an old pack could still look like the active public contract after lane drift,
2. and a newer revalidated pack could exist without formally retiring the older one.

Those are not process-only concerns.
They are ordinary ways a careful migration bundle still turns into a misleading downstream surface.

## Why this beat nearby work again

The archive already had enough to say:

- where hazards came from,
- what imports and source heads backed them,
- which follow-through and scope truths remained partial,
- whether a pack was ready to freeze or export,
- and which deviations or warnings were still active.

What it still lacked was one compact way to say:

- “this pack was valid once but now needs revalidation,”
- “this pack is still readable but no longer current enough to freeze or export as the active contract,”
- and “a newer current pack now supersedes this older one.”

That is a real product refinement, not just more governance vocabulary.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — stronger again because it now treats pack perishability and supersession as first-class contract surfaces.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
