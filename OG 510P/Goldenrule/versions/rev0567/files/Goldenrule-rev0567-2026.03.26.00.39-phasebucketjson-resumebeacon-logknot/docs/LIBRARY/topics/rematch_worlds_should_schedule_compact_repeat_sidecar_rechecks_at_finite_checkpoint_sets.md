# Rematch worlds should schedule compact repeat-sidecar rechecks at finite checkpoint sets

## Claim
Compact repeat-sidecar maintenance should be driven by a small pre-registered checkpoint set, not by per-append reevaluation.

## Why
The archive now has enough measured structure that compact repeat-sidecar changes happen only at a few meaningful places.

First, routine page births are already sparse: they land every 16 unique appends starting at append 15. That spacing is at least as wide as the current robust dwell presets, so page-birth checks are already compatible with the archive's anti-churn defaults.

Second, the uncertainty-robust dwell-9 preset only ever needs eight possible transition checkpoints across the whole measured 0.15-0.25 repeat band: 24, 47, 63, 111, 143, 159, 230, and 239. The broader dwell-16 preset compresses that to seven checkpoints. So even when repeat volume is only approximately known, the implementor still does not need a per-append planner.

Third, four structural checkpoints are load-bearing because they change the compact-state ordering or widen the route-block bitmap: 79, 111, 191, and 239. Those are the places where route blocks first overtake filters on compact state, lose that lead at the first bitmap cliff, regain it before the second cliff, and lose it again at the second cliff.

Finally, when rewrite count is the real bottleneck, the practical four-transition mode at the focal 0.18 repeat horizon only rewrites at 56, 111, 159, and 239. That means even the budgeted planner can be implemented as a finite checkpoint schedule.

## Implementor rule
- Keep a routine page-birth checkpoint stream at 15, 31, 47, 63, and every 16 appends after that.
- Treat 79, 111, 191, and 239 as mandatory structural recheck points whenever the archive is operating near marginal repeat budgets.
- For the uncertainty-robust default, pre-register the finite union checkpoint set instead of polling every append.
- For the practical four-transition mode, hard-code the rewrite boundaries 56, 111, 159, and 239.
- Do not pay continuous planning cost for a frontier that only changes at a small number of measured checkpoints.

## Minimal takeaway
The archive should maintain compact repeat sidecars with sparse checkpoint sets, not with per-append reconsideration.
