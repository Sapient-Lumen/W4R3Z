# Rematch worlds need delta-budget frontiers

The materiality and delta-frontier work already says that a declared smallest effect of interest (`delta`) changes how rematch top-gap panels are interpreted. The next compact improvement is to make the simulation-cost consequence explicit too.

In the current proxy, the extra paired-seed budget needed to close all unresolved top panels is not a monotone function of `delta`. Small changes in the declared indifference zone can change which panels remain unresolved and whether they would be cheapest to close as a materially better leader or as a practical tie.

That means a single “budget to certify” number is no longer enough once a practical-equivalence contract exists. The inheritor needs a compact frontier over a plausible `delta` band:

- how many panels are already closed at each `delta`,
- which panels remain unresolved,
- and the approximate extra paired-seed budget needed to close the residue.

This should not be used to choose `delta` opportunistically after seeing the data. The point is the opposite: keep scientific materiality and simulation cost separate, but surface their tradeoff openly.

So the contract should become: every rematch benchmark that publishes delta frontiers should also publish a compact delta-budget frontier over the plausible smallest-effect band.
