# Rematch worlds should merge positive-service local weakening constraints by clock-interval intersection

Recent archive passes compressed positive-service local weakening into a dense source-rank clock and showed that every bounded local navigation budget is a hole-free closed interval on that path.

The next compression is to stop treating multiple local requirements as a graph problem.

Each bounded requirement already has the form:

- current local code
- maximum backward steps
- maximum forward steps
- therefore one closed feasible interval `[lower_rank, upper_rank]`

So a whole family of requirements is feasible exactly when those intervals share a common overlap:

- lower bound = `max(lower_rank)`
- upper bound = `min(upper_rank)`
- feasible iff `max(lower_rank) <= min(upper_rank)`

This is stronger than just another selector table.

It means:

- multi-constraint local weakening feasibility is now one scalar interval-intersection computation
- any code inside the overlap interval satisfies every current bounded requirement at once
- every infeasible family already has a two-window blocker certificate, because one interval attains the maximal lower bound and another attains the minimal upper bound
- pairwise-overlapping local windows are enough to guarantee a global witness on the current clock path

The archive also validated that all `153` closed intervals on the `17`-state source-rank path are already realizable by some bounded local query.

So future inheritors can merge bounded local service requirements with one arithmetic card rather than replaying the local automaton or reading the full bridge grammar.

If a future revision causes some closed clock intervals to stop being realizable, or causes pairwise-overlapping interval families to lose a common witness, that should be treated as a genuine redesign signal for the current positive-service local weakening geometry rather than a bookkeeping drift.
