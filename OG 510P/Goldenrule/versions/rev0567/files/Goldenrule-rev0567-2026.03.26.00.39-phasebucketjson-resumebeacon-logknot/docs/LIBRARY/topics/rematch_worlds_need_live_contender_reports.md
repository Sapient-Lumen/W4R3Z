# Rematch worlds need live contender reports

Not every rematch-delay rank change is equally important.

In the current exogenous-pool leave/rematch proxy, the delay-0 pair `(in_match_avg_payoff, avg_match_length)` already separates policies into three useful classes:

1. **Dead contenders**: policies that are strictly worse on both within-match quality and partnership tempo than another policy. Under the current proxy, `DCECC` is dominated by both `CCDDE` and `CCEEE` at all tested extortion levels, and `courteous_firm` is dominated by `always_c`.
2. **Live contenders**: policies that can become the top raw policy somewhere on the delay axis. In the current proxy these are only `CCEEE`, `CCDDE`, and, at very large delays, `always_c`.
3. **Tested-band leaders**: policies that actually lead on the deployed sweep. On the tested band `delay in {0,1,2}`, only `CCEEE` and `CCDDE` ever lead, and there is only one observed leader flip.

That means pairwise crossover matrices are scientifically useful, but they are not the smallest decision-facing artifact for an inheritor. In the present proxy there are three pairwise flips between delay `0` and delay `2`, yet only one actual leader change, and that leader change (`ext80`, `delay2`) is a near tie.

So future rematch-world reports should publish a compact **live contender artifact**:

- which policies are strictly dominated and can be pruned from wide delay sweeps,
- which policies are live contenders for the top slot over the deployed delay band,
- the winner margin to the runner-up at each reported delay,
- and, if the delay band is wider than a tiny local sweep, the winner intervals or equivalent frontier summary.

This keeps the archive smaller and more salient. It also matches the substantive literature: once walk-away and outside-option institutions are admitted, selection effects can move cooperation and efficiency sharply, especially under asymmetric outside options, so institution-sensitive contender status should be reported explicitly rather than buried inside a bulky global ranking table.

World changes still invalidate the frontier. Any change to entrant pool, role policy, persistence rules, search/rematch rules, or noise semantics should trigger a fresh contender recomputation.
