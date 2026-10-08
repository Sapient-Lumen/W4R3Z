# Virtue vs. Strategy: Why the Distinction Is Load-Bearing

## The question

This archive distinguishes between a **virtuous agent** — one that cooperates as
an expression of what it is — and a **strategically cooperative agent** — one that
cooperates because cooperation has been computed to be the locally optimal play.

Why does this distinction matter for a formal research program?

## The short answer

Because the Golden Rule is not a strategy recommendation. It is a claim about the
*source* of cooperative behavior. An agent that cooperates from goodwill behaves
differently at the boundary conditions than an agent that cooperates from
calculation — and the boundary conditions are exactly where extortion, noise, and
partner asymmetry make the difference visible.

## The formal consequence

A strategically cooperative agent will defect when:
- the discount factor drops below its cooperation threshold,
- the opponent is identified as a defector with sufficient confidence,
- the payoff gap between exploitation and cooperation exceeds its tolerance.

A virtuous agent maintains cooperative posture under conditions where defection
is strictly payoff-dominant, absorbs some exploitation rather than retaliating
beyond what repair requires, and treats repair channels as obligations rather than
optional tactical moves.

These behaviors are distinguishable in the artifact record. The anti-vampire
scorecard (see `anti_vampire_scorecard_spec.md`) is partly designed to expose this
gap: payoff-only search will find strategically cooperative agents; only a
scorecard that includes payoff gap, recovery behavior, and repair-channel integrity
can distinguish virtue from strategy-that-mimics-virtue under pressure.

## The philosophical grounding

The distinction tracks a long debate in moral philosophy between:
- **Consequentialist** cooperation: behave cooperatively when the expected payoff
  sum is positive. Cooperation is instrumentally justified.
- **Deontological / virtue-theoretic** cooperation: behave cooperatively because
  the other is an end in themselves, not a means to your payoff. Cooperation is
  categorically expressed.

The Golden Rule belongs to the second family. "Do unto others as you would have
them do unto you" is a role-reversal test, not a payoff calculation. It asks: would
you endorse receiving this treatment? — not: does this treatment maximize joint
surplus?

This is why the universalization baseline (see `golden_rule_inheritor_brief.md`,
build item 4) matters independently of self-play performance. A strategy can achieve
high self-play while still being extractive in a mixed population. The universalization
test asks: what if everyone played this strategy? This is categorically different from
asking: does this strategy do well when paired with itself?

## The danger of flattening the distinction

If "virtuous agent" is replaced by "cooperative strategy" and "vampire" is replaced
by "adversarial agent," the vocabulary stops tracking the distinction that the
project exists to study.

A cooperative strategy is defined by its behavior. A virtuous agent is defined by
the source of that behavior. These are not equivalent. A project that flattens this
distinction will find strategies that optimize cooperation metrics while losing the
ability to distinguish whether anything like the Golden Rule is being expressed.

The vocabulary is not sentiment. It is a research commitment.

## Practical implication for search

When designing search objectives: do not optimize for cooperative behavior. Optimize
for the conditions that make a virtuous posture *viable* — meaning: survives
extortion without degenerating into pure retaliation, recovers toward cooperation
after shocks, does not exploit Always-Cooperate even when it is payoff-optimal to do
so.

The second objective is harder. It is also the correct one.

## Further reading (in this archive)

- `golden_rule_inheritor_brief.md`: build order grounded in this distinction
- `anti_vampire_scorecard_spec.md`: operationalizing virtue vs strategy in artifacts
- `memory_one_tradeoff_against_extortion.md`: empirical evidence that the tradeoff
  is real and not eliminable within memory-one search
- `search_and_extortion.md`: the metric trap — maximizing own score ≠ resisting vampirism
