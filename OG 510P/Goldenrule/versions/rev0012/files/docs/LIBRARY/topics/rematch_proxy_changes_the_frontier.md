# A Minimal Rematch Proxy Already Changes the Exit Frontier

The archive now has one more local result that matters for tranche selection:

- In a **fixed dyad**, unilateral exit alone did not rescue Golden-Rule-like behavior.
- In a **minimal leave/rematch proxy**, nice-start exit policies become genuinely competitive.

That distinction is exactly why the next implementor should build a world mechanic, not just widen search in the old one.

## What the local proxy says

The snapshot in `artifacts/reports/partner_choice_proxy_snapshot_20260306.{md,json}` evaluates all deterministic `memory_one_exit` policies in a small outside-option proxy:

- the focal agent meets either `extortion_chi3_v1` or `mem1_generous_tft_v1`,
- matches end after 50 rounds or upon exit,
- after a match ends, the focal agent rematches from the same exogenous pool,
- rematching can cost 0, 1, or 2 dead rounds.

Under that proxy:

1. **Nice-start exit now matters.** A cooperative-first leave/rematch style can beat both naive staying and first-defect trap policies on overall payoff.
2. **A compact handoff baseline exists.** `mem1_exit_after_break_v1` (`CCEEE`) is easy to explain: cooperate first, keep cooperating after `CC`, leave after any non-`CC` signal.
3. **World mechanics drive the reversal.** The same broad policy shape that looks weak in a fixed dyad becomes strong once bad matches can be escaped and replaced.

## Why this is important

This is the missing bridge between two earlier archive conclusions:

- “Unilateral exit is not partner choice” remains true.
- But rematching is already enough to change the ranking in a way the eventual engine should care about.

So the next step is not “search more exit policies in the old world.”
It is:

1. promote the proxy into an engine-supported world,
2. make the partner pool endogenous,
3. then rerun the same anti-extortion / anti-vampire scorecards.

## What not to overclaim

This proxy is **not** yet partner choice in the full sense discussed by `RS-GR-003` and `RS-GR-005`.
It still lacks:

- endogenous assortment,
- population feedback,
- reputation spillovers,
- market thickness effects,
- and mutual partner selection.

Treat it as a **design probe**, not as the finished scientific world.

## Implementor guidance

1. Keep `mem1_exit_after_break_v1` as a compact baseline when the rematch world lands.
2. Preserve the nice-start filter in any Golden-Rule-facing scorecard.
3. Canonicalize unreachable post-exit parameters in rematch-enabled search spaces; the proxy already shows that many `CCE**` variants are behaviorally identical.
4. Once the real rematch world exists, compare four families directly:
   - memory-one no-exit,
   - fixed-dyad `memory_one_exit`,
   - focal rematch proxy,
   - endogenous rematch world.

The practical handoff is simple:

> Build the rematch world next. The archive now has enough local evidence that this is not optional polish; it changes what counts as a good policy.
