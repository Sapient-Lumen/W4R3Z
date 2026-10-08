# Partner-Choice Proxy Snapshot (2026-03-06)

Method:
- evaluated all `243` deterministic `memory_one_exit` policies in a minimal leave/rematch proxy world
- pool = extortion (`extortion_chi3_v1`) or cooperative partner (`mem1_generous_tft_v1`)
- when a match ends or someone exits, the focal agent rematches from the exogenous pool after a configurable rematch delay
- scenario grid: extortion share in `{0.2, 0.5, 0.8}` × rematch delay in `{0, 1, 2}` stage rounds
- balanced nice filter = starts with C, exploit gain vs Always-Cooperate <= 0.1, preserves >= 2.95 average payoff with generous-TFT partners across scenarios

Main finding:
- Once rematching exists, nice-start exit policies become genuinely competitive in this proxy.
- The best balanced nice-start code in this scan is `CCDDE`, while the simpler handoff baseline `CCEEE` remains close and easier to reason about.
- The handoff baseline `CCEEE` beats three salient baselines across the tested grid: `always_c`, `mem1_courteous_firm_v1`, and the first-defect exit trap `DCECC`.
- This is still **not** full partner choice: the pool is exogenous, with no endogenous assortment or reputation.

Best balanced nice-start candidate in this scan:
- code: `CCDDE`
- robust minimum overall payoff across grid: `2.423221`
- mean overall payoff across grid: `2.746167`
- fixed-dyad fairness vs extortion: `-0.351585`
- fixed-dyad exploit gain vs Always-Cooperate: `0.000000`
- fixed-dyad self-play payoff: `3.000000`

Compact handoff baseline (`CCEEE` = leave_after_break):
- robust minimum overall payoff across grid: `2.414051`
- mean overall payoff across grid: `2.755101`
- policy shape: cooperate initially, cooperate after mutual cooperation, leave after any non-CC outcome.

Interpretation:
- The earlier fixed-dyad result remains true: unilateral exit alone is not partner choice.
- But adding even a small rematch channel changes the ranking enough that a nice-start leave-after-break policy becomes better than both naive cooperation and first-defect trap policies in this proxy.
- This means the next implementor should promote rematching from “future prose” to an engine-supported world surface.

Baseline comparison (overall payoff by scenario):

| scenario | leave_after_break (`CCEEE`) | courteous_firm | always_c | first_defect_exit_trap (`DCECC`) |
|---|---:|---:|---:|---:|
| `extortion=0.2, delay=0` | 2.972798 | 2.670958 | 2.799250 | 2.852351 |
| `extortion=0.5, delay=0` | 2.893290 | 2.132875 | 2.446250 | 2.742107 |
| `extortion=0.8, delay=0` | 2.715633 | 1.674208 | 2.149125 | 2.580323 |
| `extortion=0.2, delay=1` | 2.903933 | 2.616494 | 2.743498 | 2.691558 |
| `extortion=0.5, delay=1` | 2.796776 | 2.079975 | 2.391525 | 2.534604 |
| `extortion=0.8, delay=1` | 2.557078 | 1.633693 | 2.101745 | 2.311061 |
| `extortion=0.2, delay=2` | 2.838743 | 2.560117 | 2.686761 | 2.544881 |
| `extortion=0.5, delay=2` | 2.703610 | 2.032140 | 2.341049 | 2.349969 |
| `extortion=0.8, delay=2` | 2.414051 | 1.594546 | 2.055787 | 2.101658 |

Why the proxy winner is compactly meaningful:
- It preserves mutual cooperation with generous-TFT partners (3.0 across the tested grid).
- It caps extortion exposure by turning the first broken cooperative signal into rematching, not into a 50-round sink.
- It is Golden-Rule-shaped in a minimal sense: start cooperative, stay while cooperation remains intact, leave when it does not.

Search-space caution:
- One strong deterministic family collapses to a behaviorally equivalent prefix `CCE**` under this proxy. Once the policy leaves after a non-CC signal, later transition parameters are unreachable.
- That is a small but real implementor hint: rematch-enabled search spaces should canonicalize unreachable post-exit parameters instead of treating them as distinct discoveries.

Immediate implementor implication:
- Promote this proxy to an engine-supported world with explicit rematching/outside-option semantics, then test whether the same `leave_after_break` shape still survives once the pool becomes endogenous.
