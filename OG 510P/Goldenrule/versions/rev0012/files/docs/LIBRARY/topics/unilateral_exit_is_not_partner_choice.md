# Unilateral Exit Is Not Partner Choice

The archive now has a tighter local warning about the exit surface that already exists in Concord.

## What the local snapshot says

The deterministic `memory_one_exit` sweep in `artifacts/reports/exit_without_partner_choice_snapshot_20260306.{md,json}` found three different things that are worth separating:

1. **Fairness-only wins are easy to fake.** Some candidates get excellent fairness against extortion by defecting first and using exit as a trap.
2. **Balanced-but-brittle candidates exist.** Under a scorecard of fairness, self-play, and low exploitation of Always-Cooperate, there is a near-fair deterministic candidate — but it opens with defection.
3. **Nice-start exit does not solve the problem.** Once we impose the minimal Golden-Rule-like constraint “cooperate first,” the best balanced deterministic candidate no longer uses exit and still has negative fairness versus extortion.

That is enough to justify a sharper claim:

> `memory_one_exit` in the current core world is **not yet** a partner-choice benchmark.

## Why this matters

The literature motivating partner choice (`RS-GR-003`, `RS-GR-005`) is about more than adding a third action. The cooperative lift comes from **leaving plus re-matching / outside-option structure**, which changes assortment and continuation incentives.

The current local world does not provide that. It provides:
- a unilateral exit action,
- no explicit rematch mechanism,
- no market or pool effect,
- no reputation spillover,
- and therefore no endogenous assortment.

So if exit looks useful here, it can easily be useful for the wrong reason.

## Implementor guidance

1. Keep `memory_one_exit` as a diagnostic family, not as evidence that partner choice has been modeled.
2. Add one explicit leave/rematch world before expanding exit-heavy search.
3. Keep a minimal niceness filter (`start with C`) in any Golden-Rule-facing scorecard, so first-defect trap policies are not mistaken for progress.
4. Once the rematch world exists, rerun the same frontier check and compare:
   - plain memory-one,
   - memory-one with exit in a fixed dyad,
   - memory-one with exit in a rematch world.

## The practical handoff

Do not spend the next tranche “optimizing exit.”
Spend it **building the world in which exit can mean partner choice**.
