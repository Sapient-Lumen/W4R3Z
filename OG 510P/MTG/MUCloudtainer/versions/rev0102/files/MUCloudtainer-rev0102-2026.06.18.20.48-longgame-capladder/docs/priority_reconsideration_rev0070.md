# Priority reconsideration — rev0070

## What changed

The population matrix is no longer just complete; it has a fail-closed precision gate. The doubled run rejected every size/life cell for imprecision, which prevents accidental promotion from noisy means.

The evidence migration path also became less confused: generated `data/` references no longer masquerade as live blockers, and missing compact derivatives are now exposed as their own retention class.

## Highest-value next work

```text
1. Build a faster batched population runner so the 2×3 matrix can reach narrow confidence intervals.
2. Redirect active raw-path references in scripts/docs/tests to the evidence index and compact derivatives.
3. Create compact derivatives for the two newly exposed missing-derivative blockers.
4. Only then migrate the first bulky transition family out of the linked core.
5. Keep new hand-written policy work paused until a population-security gate can actually pass or fail with adequate precision.
```

## Explicit depriorities

```text
claim promotion from rev0070 mean scores
more named duel repairs before precision improves
new raw transition tables without compact derivatives
large doctrine files that do not change tests, gates, or byte movement
```
