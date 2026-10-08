# 27 — Global HOT Promotion Table (v0.19)

Goal: make “global hot deltas” deterministic and bounded, so attention routing isn’t vibes.

## Promotion classes (highest wins)
### Class M (Mandatory)
Always promoted and always shown:
- mode/strictness changes
- leases touching your TOUCH scope
- selected patch changes
- certified counterexamples
- verifier failures on canonical checks

### Class H (Hot by score)
Promote if `hotness >= H_THRESHOLD` (default 60).

### Class V (Voted hot)
Promote if:
- explicit `hot{ID=...}` vote, AND
- `hotness >= V_THRESHOLD` (default 40), AND
- not evicted/obsolete

### Class E (Exploration hot)
Promote temporarily (1–2 view cycles) if discovery produced:
- a certifiable CE
- a new E# refuting selected patch
- a deadlock-resolving concrete next action

## Boundedness rules
- Global HOT size cap: `HOT_MAX = 8`
- Per-class caps: H up to 6, V up to 4, E up to 2 (Mandatory is naturally small)
- If full, demote lowest-hotness non-mandatory first.

## “Noisy hot” suppression
Suppress (unless mandatory) if item:
- lacks stable ID
- is pure discussion with no action/evidence/patch/CE
- repeats already-hot info without new signal

## Human pin
Human can pin up to 3 HOT items explicitly; pinned items ignore caps (appear after H0).

See also: 46_controlled_exploration_policy.md and 48_exploration_metrics_and_tuning.md
