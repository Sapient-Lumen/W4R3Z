# Rematch worlds should choose bounded local weakening compromise witnesses by median projection

If a bounded positive-service local weakening requirement family is feasible, then compromise witness choice for multiple preferred local codes should be treated as a path `L1` problem rather than a bespoke graph search.

On the current source-rank path, the unconstrained `L1` argmin set for a batch of preferred local codes is the median interval of their source ranks. Constraining the choice to a feasible overlap interval adds no new geometry: the full feasible argmin set is exactly the projection of that median interval onto the feasible overlap interval.

Operational consequences for inheritors:

- odd preference bundle widths always yield a unique optimal feasible witness;
- even preference bundle widths may yield a contiguous tie interval, but never a disconnected argmin set;
- infeasible families should still fail with the same blocker certificate from the feasibility-intersection law;
- and batch compromise selection should therefore be implemented as median extraction plus interval projection, not replay of the local weakening chain.
