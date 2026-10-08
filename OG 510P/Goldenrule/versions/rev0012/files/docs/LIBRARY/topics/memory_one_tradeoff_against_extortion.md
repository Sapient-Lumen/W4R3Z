# Memory-One Tradeoff Against Extortion

Local analytic search now suggests a tighter claim than the earlier “payoff-only metrics are bad” note:

- within a 200k random sample of memory-one strategies,
- scored against extortion, self-play, Always-Cooperate, and Generous TFT,
- no sampled candidate simultaneously achieved:
  - nonnegative fairness versus extortion,
  - self-play payoff at least `2.5`,
  - and low exploitation of Always-Cooperate (`gain <= 0.1`).

This is not a proof of impossibility. It is a compact empirical warning.

## Why this matters

A Golden-Rule-like policy is trying to do at least three things at once:
1. refuse extortion,
2. preserve stable cooperation with peers,
3. avoid becoming a parasite on naive cooperators.

The current local memory-one evidence suggests that these goals are sharply tensioned inside the plain memory-one space.

## Shape of the best local witness

The current witness baseline (`examples/strategies/mem1_courteous_firm.json`) has a recognizable structure:
- `p_cc` almost 1: keep cooperation once established,
- `p_dd` near 0: do not linger in mutual defection,
- `p_dc` high: repent quickly after your own defection if the other side cooperates,
- `p_cd` moderate rather than high: do not instantly resume full trust after being exploited.

That shape is worth keeping even if the exact parameters move.

## Implementor guidance

1. Treat this as evidence for **phased expansion**, not for despair.
2. Add one modestly richer family next, not ten. Good candidates are:
   - reactive-2 / recency-weighted memory,
   - `memory_one_exit`,
   - a minimal leave-and-rematch world.
3. Re-run the same scorecard after each expansion. Do not compare larger spaces only on best payoff.
4. Keep heterogeneous-space checks in view: richer memory can improve welfare and still lose in competitive adaptation.

## Concrete next test

Run the same scorecard in three adjacent spaces:
- plain memory-one,
- memory-one with exit,
- one small longer-memory family.

If only the richer families can push the extortion fairness gap near zero while retaining high self-play and low exploitation of cooperators, that is a strong tranche-selection signal.
