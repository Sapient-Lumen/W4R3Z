# Rematch worlds need declared budget-family profiles, not "all caps we touched"

The archive now has shortlist guardrails and declared priority profiles, but there is still one earlier judgment that can silently decide the whole outcome: **which budget-family of extra-seed caps is being treated as binding?**

The new derived report in `artifacts/reports/rematch_proxy_delta_family_viability_snapshot_20260306.{md,json}` makes that dependence explicit for the current leave/rematch proxy.

A tempting mistake is to define the family implicitly as “every cap we happened to analyze.” In this proxy, that would mean forcing the low-delta anchor to survive not only caps `10/20/50/100`, but also cap `4`.

That sounds innocent, but it changes the archive’s options sharply.

- For the exact family `10/20/50/100`, the low-delta hazard-clear cores can tolerate a width floor up to `0.00156` before all candidates disappear, and up to `0.00129` while still leaving at least two candidates.
- For the exact family `4/10/20/50/100`, those numbers collapse to `0.00032` and `0.00029`.
- So at the archive’s current strict width floor of `0.0010`, the `10/20/50/100` family still supports `2` sub-`0.01` candidates, while the `4/10/20/50/100` family supports `0`.

That means the budget-family declaration is not just bookkeeping. It decides whether a robust low-delta scalar constant exists at all.

The implementor consequence is simple:

1. declare the exact budget-family profile first,
2. justify why those caps matter operationally,
3. then apply width floors, hazard filters, and priority profiles inside that family,
4. and never let “all caps we touched” stand in for a substantive family choice.

In the current proxy, cap `4` is not merely a stricter version of the same world. It is a fragmentation regime. Folding it into the default required family silently converts a viable shortlist problem into a no-anchor problem.
