# Centralized social-credit-style scores are not innocent reputation baselines

Recent evidence suggests that a centralized scalar reputation is not a neutral shortcut for “more information”.

- `RS-GR-152` examines social-credit-score availability in economic interaction tasks.
- The paper reports that exposing those scores lowers trust and reduces cooperation rather than simply helping people sort better partners.
- It also reports that score-based judgments create persistent perception biases that resist directly contradictory behavioral evidence.
- The paper further reports that these effects disproportionately disadvantage lower-scored individuals, amplifying inequality and polarization.

## Why this matters for Concord

A future benchmark could easily import a hidden institutional choice:

> use one centralized scalar reputation and treat it as the default reputation world.

That would be a mistake.
A central score can crowd out direct experience, harden stale judgments, and make “rehabilitation” or “fresh behavior” much weaker than in a world with local or revisable reputations.

So a centralized score is not just a compact encoding of reputation.
It is a stronger institution with its own failure modes.

## Minimal implementor handoff

If Concord ever adds a social-credit-like or centralized-score lane, publish at least:

1. whether the scalar score is advisory or binding for partner choice / help / punishment;
2. whether direct interaction evidence can override the score, and on what timescale;
3. how quickly new behavior updates the score versus how sticky prior penalties are;
4. whether counterparties see raw recent behavior, the scalar score only, or both.

Without that split, future results can attribute lower trust or harsher exclusion to “reputation” in general when the real driver was centralized score governance.
