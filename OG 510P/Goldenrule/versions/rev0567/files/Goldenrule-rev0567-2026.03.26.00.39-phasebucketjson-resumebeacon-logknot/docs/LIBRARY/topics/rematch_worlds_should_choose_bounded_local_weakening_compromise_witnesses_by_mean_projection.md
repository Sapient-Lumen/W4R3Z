# Rematch worlds should choose bounded local weakening compromise witnesses by mean projection

If a bounded positive-service local weakening requirement family is feasible, then compromise witness choice for multiple preferred local codes can also be treated as a path `L2` problem rather than a bespoke graph search.

On the current source-rank path, the unconstrained squared-distance argmin set for a batch of preferred local codes is the set of integer ranks nearest to the arithmetic mean of their source ranks. Constraining the choice to a feasible overlap interval adds no new geometry: the full feasible argmin set is exactly the nearest feasible integer point or adjacent feasible integer pair obtained by projecting that mean rank onto the feasible overlap interval.

Operational consequences for inheritors:

- ties still appear only for even preference bundle widths, but they never exceed two adjacent local codes;
- compared with the `L1` median law, the `L2` objective sharply reduces tie burden on the current archive geometry;
- the objective is genuinely different from `L1`, so it can move the chosen witness toward outliers and should be treated as a separate compromise semantics rather than a mere tie-break rule;
- infeasible families should still fail with the same blocker certificate from the feasibility-intersection law;
- and batch compromise selection under squared path loss should therefore be implemented as mean extraction plus interval projection, not replay of the local weakening chain.
