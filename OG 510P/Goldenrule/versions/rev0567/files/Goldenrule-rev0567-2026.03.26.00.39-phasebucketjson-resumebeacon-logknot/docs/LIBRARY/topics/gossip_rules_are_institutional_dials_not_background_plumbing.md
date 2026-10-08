# Gossip rules are institutional dials, not background plumbing

Recent private-reputation work sharpens how Concord should treat gossip once reputation lanes become live.

- `RS-GR-137` studies indirect reciprocity with **private reputation** and explicit **gossip transmission**.
- The paper reports that gossip can break the deadlock created by disagreeing private reputations, suppress defection, and stabilize cooperation.
- More frequent gossip improves cooperation by increasing information flow and reducing disagreement over reputations.
- But the paper also reports a warning: the effect of **trust weight** is **non-monotonic**, and dual-source gossip helps substantially only when trust weight is already high.

## Why this matters for Concord

Once a world includes gossip, the benchmark is no longer just “reputation, but with extra communication.”

Gossip frequency, source count, and trust/merge rules help determine whether reputations converge, fragment, or become over-amplified.
That makes gossip part of the institution itself, not just a reporting or logging layer around it.

## Minimal implementor handoff

If Concord enables gossip in a reputation world, publish at least:

1. gossip cadence / opportunity frequency,
2. gossip fan-in (single source, dual source, or broader),
3. trust weighting / merge rule for second-hand reports,
4. whether agents retain independent judgment or mostly copy received beliefs,
5. one no-gossip baseline for comparison.

Without that compact contract, “reputation plus gossip improved cooperation” is too underspecified to inherit safely.
