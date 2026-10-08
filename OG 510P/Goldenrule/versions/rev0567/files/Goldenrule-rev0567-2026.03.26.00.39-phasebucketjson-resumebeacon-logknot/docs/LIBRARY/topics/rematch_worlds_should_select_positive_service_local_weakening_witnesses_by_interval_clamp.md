# Rematch worlds should select positive-service local weakening witnesses by interval clamp

Once a family of bounded positive-service local weakening requirements is feasible, the archive no longer needs any extra local graph search to choose a satisfying state. The feasibility-intersection law already reduces the family to a closed source-rank interval, so witness choice is just interval arithmetic.

The practical rule is tiny:

- earliest feasible witness: choose the lower bound,
- latest feasible witness: choose the upper bound,
- closest feasible witness to any preferred local code: clamp the preferred code's source rank into the overlap interval,
- midpoint witnesses: choose the lower or upper median of the same interval.

This matters because it closes the loop from local service requirements to a concrete implementable state without reopening the local staircase tables. Selection adds no new failure mode beyond interval disjointness; if the family is infeasible, the old two-window blocker certificate remains the whole story.

Future inheritors should treat any deviation from clamp behavior as a redesign alarm for the current positive-service local automaton.
