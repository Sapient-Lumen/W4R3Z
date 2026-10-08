# Crate ecosystem pathfinder watch boundaries — 2026-03-20

This note exists to keep the new **decision-aging** work in **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** from dissolving into neighboring lanes.

## What this watch layer is

The watch layer is the part of P-0509 that answers:

- which later events reopen review of a frozen starter set,
- how long the frozen answer may age quietly,
- and what the current watch state is.

Its center of gravity is still **crate-choice stewardship**, not general security scanning or maintenance analytics.

## What it is not

### Not P-0011 Crate Health

Health artifacts can be imported as triggers.
But P-0509 watch state is about **what that imported change means for a previously frozen choice**, not about re-owning the health lane.

### Not P-0017 Trust Lens

Trust/security signals can fire revisit triggers.
But the watch layer should not become a disguised trust score or malware-detection platform.

### Not P-0514 upgrade-pack revalidation

Upgrade packs ask whether one release-to-release migration contract is still fresh and superseded.
P-0509 watch state asks whether a **crate-choice decision** is still approved for one task lane.

### Not P-0515 off-ramp planning

A fired trigger can imply that an off-ramp may be needed.
That does not mean the watch layer should absorb successor mapping, sunset recipes, or checked exit bundles.

### Not a silent auto-recommender

The watch layer may say `review_due` or `invalidated`.
It must not silently replace the chosen starter set with the next-ranked crate.
Human review remains part of the contract.

## Positive boundary tests

A feature belongs in this watch layer if it answers one of these questions:

1. **Which event classes reopen review of a frozen decision?**
2. **How long may the frozen decision age quietly?**
3. **What is the current watch state of the frozen decision?**
4. **Was the old decision explicitly superseded by a newer reviewed one?**

If a feature instead answers:

- “how healthy is this crate in general?”,
- “which crate should replace it now?”,
- “how do we migrate off it?”,
- or “how do we verify a concrete release-to-release upgrade?”

then it likely belongs to an adjacent lane.

## Design rule

Future passes must keep these four things separate:

- **freshness window**,
- **revisit trigger**,
- **watch state**,
- **replacement decision**.

Do not let the archive quietly flatten them into one fake “starter set drift” story.
