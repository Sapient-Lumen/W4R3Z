# Rematch worlds should choose exact-uncertainty service relaxations by local upgrade witness

When the archive already carries the width-only weakening SLA staircase, the next operator question is local rather than global: from the **current** service target, which axis unlocks next if the target is relaxed slightly, and how much relaxation does that require?

The archive should answer that question from the two threshold ladders directly.
For any current target:

- compute the current support signature `(exact horizon, suffix horizon)`
- read the next exact-only threshold and the next suffix-only threshold
- the **larger** of those two thresholds is the first additional support unlocked by relaxing the target
- equality is the lone shared diagonal unlock at `1/91`

In the current menu every nonterminal positive-service state has a unique local witness:

- `10` states are suffix-first
- `5` states are exact-first
- `1` state is shared-diagonal-first
- and the terminal state `E6_S11` has no further positive-service unlock

So the inheritor no longer needs to reread the whole staircase to plan the next relaxation step; they only need the current signature plus the next exact/suffix threshold pair.
