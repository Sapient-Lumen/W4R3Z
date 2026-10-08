# Reputation granularity is a world contract, not just score resolution

Recent indirect-reciprocity work adds a compact warning for Concord's future reputation lanes.

- `RS-GR-141` reports that stable cooperation need not live inside a binary good/bad reputation regime.
- The paper's experimental and theoretical results support a **three-level** reputation picture (`good`, `neutral`, `bad`) with **gradual** upgrading and downgrading rather than all-at-once flips.
- In that regime, justified defection against a bad recipient can leave the donor's reputation unchanged instead of forcing a crude binary jump.

## Why this matters for Concord

A future reputation lane should not assume that adding more bins is merely cosmetic scoring detail.

Binary, ternary, and gradual reputation systems create different forgiveness paths, different punishment semantics, and different recovery trajectories after noise.
A policy that looks harsh, forgiving, or robust under one reputation alphabet may look different under another.

So reputation granularity belongs in the world contract.
It is not just a renderer choice for the scoreboard.

## Minimal implementor handoff

If Concord adds a reputation lane, publish at least:

1. the reputation alphabet (`{good,bad}` vs `{good,neutral,bad}` or other declared set),
2. whether updates are binary flips, one-step moves, or some other transition rule,
3. whether justified defection leaves reputation unchanged,
4. the recovery path length from worst state back to trusted state,
5. one binary-granularity baseline before generalizing from a richer scheme.

Without that contract, future sessions can mistake a change in reputation state space for a change in reciprocity quality.
