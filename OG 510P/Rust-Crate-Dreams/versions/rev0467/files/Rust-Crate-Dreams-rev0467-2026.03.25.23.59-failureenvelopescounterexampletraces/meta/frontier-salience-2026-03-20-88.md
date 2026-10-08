# Frontier salience snapshot — 2026-03-20 (88)

This pass did **not** add another release helper, another changelog improver, or another codemod-adjacent crate.
It deepened **P-0514 Crate Upgrade Pack Kit** one step further by making three receiver-facing truths explicit:

- **source-lineage truth** — which imported release/changelog/docs/thread surfaces were allowed to speak for hazard authority, how they were fetched, and whether they were pinned strongly enough to count;
- **hazard-arbitration truth** — what the pack does when SemVer/public-API evidence, feature-policy drift, maintainer notes, and observed behavior checks do not honestly collapse into one story;
- **active follow-through state** — which migration steps belong to the lane, which are actively requested on the current release pair, and which were only completed on an older lane.

## Main judgment

The sharper missing layer is still the **joined upgrade-support contract** above today’s substrate.
But after the previous authority/scope pass, the next false merge risk sits in three places:

1. imported human-authored release surfaces get promoted into evidence without enough source-lineage discipline,
2. adjacent authorities disagree and the pack still emits one polished winner,
3. old manual migration work gets mistaken for current-lane completion.

Those are not edge cases.
They are ordinary ways upgrade support becomes misleading.

## Why this beat nearby work again

The archive already had enough to say:

- what kind of hazard exists,
- where a machine fix touched,
- and which package/workspace lanes were in-bounds.

What it still lacked was a compact way to say:

- “this hazard authority came from a release-pinned source, not a floating nearby note,”
- “these authorities disagree, so the honest answer is abstention/manual review,”
- and “this docs/config/example follow-through was completed on an older lane and is freshly requested again now.”

That is a real product refinement, not a naming flourish.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because freezeable crate choice compounds later decisions.
2. **P-0514 Crate Upgrade Pack Kit** — now stronger again because it distinguishes source lineage, authority arbitration, and active follow-through state above generic release substrate.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth remains widely missing.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth are concrete and receiver-facing.
