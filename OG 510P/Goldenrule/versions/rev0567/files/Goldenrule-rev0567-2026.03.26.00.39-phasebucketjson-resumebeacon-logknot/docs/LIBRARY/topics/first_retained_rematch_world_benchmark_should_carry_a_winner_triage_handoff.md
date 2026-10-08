# The first retained rematch-world benchmark should carry a winner triage handoff

The archive already has the three proxy-era ingredients needed to reason about winner-side uncertainty:

- `rematch_proxy_live_contenders_snapshot_20260306.json`
- `rematch_proxy_winner_certification_snapshot_20260306.json`
- `rematch_proxy_materiality_gate_snapshot_20260306.json`

But without one compact **benchmark-facing handoff**, a future inheritor still has to reopen several reports just to answer the practical question: **which apparent leader changes are actually decision-relevant enough to care about first?**

A retained benchmark seed should therefore carry one tiny copied winner-triage handoff instead of forcing the next session to reconstruct the answer from scratch.

For the current proxy, the compact facts are already strong and small:

- the live contender union is only `CCEEE`, `CCDDE`, and `always_c`,
- the observed tested-band leaders are only `CCEEE` and `CCDDE`,
- `DCECC` and `courteous_firm` are already dominated in the tested nonnegative-delay slices,
- `8 / 9` tested panels already have certified 95% leader margins,
- only the `extortion=80, delay=2` panel remains uncertified,
- and several certified leaders already become practical ties once the smallest effect of interest reaches `0.005`.

That is the right benchmark-facing summary size.
It is much smaller than copying full per-panel tables, but much more actionable than merely pointing at three separate proxy reports.

So the retained benchmark should keep exactly one frozen winner-triage handoff with:

1. source-report digests,
2. the live contender union,
3. the dominated-policy summary,
4. certification counts plus the one uncertified panel row,
5. the materiality counts and edge panels,
6. and an explicit upgrade note saying that native endogenous rematch runs should replace this copied proxy-era handoff once real winner-side outputs exist.
