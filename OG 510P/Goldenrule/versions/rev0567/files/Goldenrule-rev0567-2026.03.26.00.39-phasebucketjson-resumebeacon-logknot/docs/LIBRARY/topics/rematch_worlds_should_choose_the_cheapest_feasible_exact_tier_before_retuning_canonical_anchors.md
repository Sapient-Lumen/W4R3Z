# Rematch worlds should choose the cheapest feasible exact tier before retuning canonical anchors

## Claim

For canonical steady-state exact-uncertainty operation, the archive should first choose the **cheapest feasible** exact tier that satisfies the declared request and only then retune among anchors `{2, 13, 25}` if the selected tier differs from the current one.

## Why this matters

The request oracle can say which tiers are feasible.
The route atlas can say how to move among canonical anchors.
What was missing was the control rule tying those together.
Without that rule, a deployment can remain unnecessarily over-provisioned after the required floor weakens just because the stronger tier is still feasible.
That wastes hard cap, checkpoints, and dwell freedom.

## Current steady-state rule

1. Run the request oracle on the declared floor, cap, checkpoint, slack, and width bundle.
2. If no tier is feasible, stop and surface the blocker.
3. Otherwise choose the cheapest feasible exact tier.
4. Hold if the current anchor already matches that tier.
5. Otherwise reuse the canonical anchor route atlas to weaken or strengthen to the selected tier.

## Exact floor-only control matrix under nonbinding budgets

- from `near_exact`:
  - floor `≤ 0.870482` → weaken to `lower_guarantee` via `2 -> 8 -> 19 -> 25`
  - floor `(0.870482, 0.980481]` → weaken to `near_optimal` via `2 -> 8 -> 13`
  - floor `(0.980481, 0.999822]` → hold at `near_exact`
- from `near_optimal`:
  - floor `≤ 0.870482` → weaken to `lower_guarantee` via `13 -> 19 -> 25`
  - floor `(0.870482, 0.980481]` → hold at `near_optimal`
  - floor `(0.980481, 0.999822]` → strengthen to `near_exact` via `13 -> 2`
- from `lower_guarantee`:
  - floor `≤ 0.870482` → hold at `lower_guarantee`
  - floor `(0.870482, 0.980481]` → strengthen to `near_optimal` via `25 -> 18 -> 13`
  - floor `(0.980481, 0.999822]` → strengthen to `near_exact` via `25 -> 2`

## Practical rule

Do not ask “what is the strongest tier we can still afford?” when the archive is choosing a new steady exact mode.
Ask “what is the cheapest exact tier that still satisfies the declared request?”
Then move only if the current anchor is not already that tier.
Use the boundary-stabilization protocol first whenever the live deployment is stranded on transient boundary `{8, 18, 19}` instead of a canonical anchor.

## Status

Derived exactly from the saved guarantee-threshold selector, request oracle, canonical-anchor path atlas, and boundary-stabilization protocol on 2026-03-08.
