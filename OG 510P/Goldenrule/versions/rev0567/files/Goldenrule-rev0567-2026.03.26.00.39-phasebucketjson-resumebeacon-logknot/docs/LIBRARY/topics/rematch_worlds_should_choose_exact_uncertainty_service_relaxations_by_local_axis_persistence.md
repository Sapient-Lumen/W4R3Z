# Rematch worlds should choose exact uncertainty service relaxations by local axis persistence

## Claim

When a width-only weakening SLA must be relaxed repeatedly, the inheritor should track the local **axis persistence horizon** of the current staircase state, not just the next unlock axis. In the current archive geometry, exact-only unlocks are singleton spikes, while nontrivial repeated-relaxation persistence appears only on suffix-only runs.

## Why

The recent local-upgrade witness and local slack-lead cards answer the pointwise question “which axis unlocks next?” But an implementor planning a sequence of SLA relaxations also needs the temporal question: “if I keep relaxing, how long does this axis remain the governing direction before a different axis takes over?”

The positive-service staircase answers that with a run decomposition over local unlock kinds.

## Current law

- The positive-service staircase has `12` local axis runs:
  - `6` suffix-only runs,
  - `5` exact-only runs,
  - `1` shared-diagonal run.
- Every exact-only run has length `1`.
- The longest suffix-only run has length `3`, from `E1_S2` through `E1_S5`.
- The unique shared-diagonal run has length `1`, at `E3_S8 -> E4_S9`.

So the current menu has an asymmetric persistence geometry:

- **exact-only leadership is always local and nonpersistent**
- **suffix-only leadership can persist across multiple consecutive relaxations**
- **shared growth is a single audited exception rather than a regime**

## Operational use

For any current width-only SLA target, compute:

- current staircase signature
- next unlock kind
- persistence steps remaining
- terminal signature after the current run completes

Then govern repeated relaxation accordingly:

- if persistence is `1`, treat the current unlock direction as a one-step opportunity rather than a stable corridor;
- if persistence is `2+`, treat the winning axis as the current relaxation corridor;
- if any future archive revision produces an exact-only run longer than `1`, or another shared-diagonal run, treat it as a real redesign of the service geometry rather than a small perturbation.

## Consequence

The inheritor no longer has to read the recent local service-relaxation stack as a sequence of unrelated local choices. It is now one short run language:

- suffix-only corridors,
- isolated exact-only spikes,
- one shared kink.
