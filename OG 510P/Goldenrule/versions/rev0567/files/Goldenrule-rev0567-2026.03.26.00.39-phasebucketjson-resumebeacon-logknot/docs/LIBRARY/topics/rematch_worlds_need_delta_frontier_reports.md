# Rematch worlds need delta-frontier reports

The materiality-gate work already shows that winner certification and practical importance are separate decisions. The next compact improvement is to stop publishing those decisions only at a couple of arbitrary `delta` values.

For each rematch top-gap panel, the current proxy can be compressed to two thresholds:

- the largest `delta` that still supports a materially better leader,
- the smallest `delta` that already supports a practical tie.

Everything in between is the only genuinely delta-sensitive band. That means downstream consumers do not need a bulky table of classifications at many hand-picked thresholds. They only need the frontier pair.

This is useful for the inheritor because `delta` should be declared for substantive reasons, not reverse-engineered from the observed gap. Publishing the frontier pair keeps the archive small while making threshold sensitivity explicit:

- if deployed `delta` is below the lower cutoff, ship a material leader;
- if deployed `delta` is at or above the upper cutoff, ship a practical tie;
- only if deployed `delta` falls inside the middle band is the panel genuinely undecided on materiality grounds.

So the contract should become: every rematch benchmark that publishes winner-certification and practical-equivalence metadata should also publish a compact per-panel delta frontier.
