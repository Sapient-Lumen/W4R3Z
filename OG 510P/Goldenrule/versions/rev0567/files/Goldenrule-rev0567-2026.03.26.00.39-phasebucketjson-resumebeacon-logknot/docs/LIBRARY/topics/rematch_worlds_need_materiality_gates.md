# Rematch worlds need materiality gates

Budget-aware winner triage is still missing one compact ingredient: a declared smallest effect of interest for the top-vs-runner-up gap.

The new derived report in `artifacts/reports/rematch_proxy_materiality_gate_snapshot_20260306.{md,json}` shows why. In the current proxy, winner certification and practical materiality are not the same thing.

Three extortion-20 panels already have statistically certified winners, but at a modest practical threshold of `delta = 0.005` they are better treated as practical ties. Conversely, the only uncertified leader flip (`ext80, delay2`) already becomes a practical tie with the current six paired seeds once the indifference zone reaches about `0.008233`, far cheaper than trying to certify a microscopic winner there.

That means future rematch benchmark artifacts should publish both:

- a winner-certification field for the top-vs-runner-up margin, and
- a practical-equivalence / indifference-zone field keyed to a declared `delta`.

With those two fields plus the existing budget-to-certify metadata, the inheritor gets a clean three-way action rule:

- materially better leader,
- practical tie,
- or unresolved panel that may justify more sampling.

This is smaller and more honest than archiving every tiny certified winner as decision-relevant, or every uncertified flip as mandatory rerun work. It turns near-tie handling into an explicit contract instead of a hidden judgment call.
