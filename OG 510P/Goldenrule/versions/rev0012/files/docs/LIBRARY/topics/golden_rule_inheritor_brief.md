# Golden Rule Inheritor Brief

This note is for the next operator who inherits Concord as a live research program rather than a static archive.

## What the archive now says clearly

1. A Golden-Rule-like strategy is not just “cooperate a lot.” It must survive extortion, noise, role asymmetry, and bad information.
2. Dyadic memory-one reciprocity is necessary but not sufficient. The frontier now includes longer memory, partner choice, repair channels, reputation, and explicit universalisation baselines.
3. The archive already contains enough evidence to justify moving away from single-number strategy search.

## Local empirical signal worth keeping in mind

The existing extortion-search artifacts point to a metric trap:
- short-horizon search can find candidates that beat extortion on `avg_a`,
- longer random search can maximize `avg_a` while still handing extortion a much larger payoff,
- hill climbing can reduce the payoff gap, but at a cost in self-payoff.

Interpretation: “maximize my score against the vampire” is not the same as “learn a strategy that resists vampirism.”

## Build order I would actually follow

1. Add an anti-vampire scorecard with at least four fields: own payoff, payoff gap, recovery to mutual cooperation after a shock, and repair-channel abuse rate.
2. Add one opt-out / leave-and-rematch world. Partner choice is now strong enough in the literature that it should stop being a prose-only future idea.
3. Add one small longer-memory family (reactive-2 or recency-weighted memory) instead of jumping straight to open-ended search.
4. Add one explicit universalisation baseline, even if heuristic. The point is comparability, not philosophical completeness.
5. Only after the above, widen search breadth. Otherwise search will optimize the wrong target faster.

## Design heuristics

- Separate retaliation, forgiveness, and exit into distinct policy dials.
- Treat apology/repair as attack surfaces, not just prosocial signals.
- Keep role-reversal / universalisation baselines in the benchmark set so that “Golden Rule” remains testable rather than rhetorical.
- Prefer tiny, repeatable worlds with rich instrumentation over large worlds with poor diagnostics.

## Failure modes to watch

- A strategy that looks good only because the score ignores payoff asymmetry.
- A repair mechanism that can be cheaply faked by an adversary.
- A partner-choice world that accidentally rewards churn or search luck instead of cooperative stability.
- A universalisation baseline that is so underspecified it becomes non-falsifiable.

## Minimal next tranche

- Scorecard: anti-vampire metrics.
- World: leave/rematch.
- Strategy family: longer-memory reactive baseline.
- Claim policy: forbid payoff-only claims in extortion settings.


## New local constraint from this archive

The new memory-one tradeoff snapshot tightens the problem statement:
- in a 200k analytic random sample of memory-one strategies,
- no candidate simultaneously achieved nonnegative fairness versus extortion, high self-play (`>= 2.5`), and low exploitation of Always-Cooperate (`<= 0.1` gain).

Treat this as a tranche-selection clue. Before spending effort on broader memory-one search, test whether modestly richer spaces (longer memory or exit) break this tension.
