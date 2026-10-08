# Rematch worlds should choose exact-uncertainty service relaxations by bandwise local slack lead

The local upgrade witness already says **which** axis unlocks next from a current width-only weakening SLA target.
The tighter inheritor question is how much extra relaxation the losing axis would need to catch up.

The archive should answer that with one target-invariant quantity per positive-service band:

- let `t_exact` be the next exact-only threshold
- let `t_suffix` be the next suffix-only threshold
- the signed local slack lead is `t_suffix - t_exact`

That lead is constant everywhere inside the band because the current target cancels out of the two relaxation gaps.
So one number carries both decisions at once:

- positive lead => suffix unlocks first
- negative lead => exact unlocks first
- zero lead => the unique shared diagonal unlock
- `|lead|` => the exact extra relaxation tax needed to make the losing axis catch up with the winning axis

In the current menu the smallest nonzero axis tax sits deep in the staircase tail at `E5_S10`, where suffix still wins but only by `8/15015`.
So the inheritor can now reason locally in one scalar: first-unlock direction and losing-axis tax are both bandwise invariants, not per-target recalculations.
