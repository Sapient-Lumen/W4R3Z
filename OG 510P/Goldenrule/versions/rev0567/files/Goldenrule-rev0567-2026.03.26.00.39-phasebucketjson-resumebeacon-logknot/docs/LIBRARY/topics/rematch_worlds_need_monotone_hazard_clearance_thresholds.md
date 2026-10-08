# Rematch worlds need monotone hazard-clearance thresholds, not just sampled caps

Once the archive has already declared an exact budget family, a width-floor band, and a delta-ceiling band, the hazard dimension should be published as a **minimum clearance threshold** whenever the guardrail is monotone in extra paired-seed budget.

That is the right contract here because the hazard intervals shrink as the added budget grows. So a candidate that clears at some cap stays clear for all larger caps; the real scientific question is not “which sampled caps did we happen to test?” but “what is the first cap at which the intended shortlist actually appears?”

The new derived report in `artifacts/reports/rematch_proxy_delta_hazard_threshold_snapshot_20260306.{md,json}` shows that, for the current leave/rematch proxy and the exact family `10/20/50/100`:

- with width floor `0.0010` and strict sub-`0.01` ceiling, the shortlist is empty for hazard caps `0..4`,
- at caps `5..9`, only `TTTMMMMUU@0.00744` clears,
- only at cap `10` does the full two-anchor low-delta shortlist appear, adding `TTTMMMMMU@0.00602`,
- and from cap `10` onward that full shortlist persists.

So the old sampled range `100, 500, 1000, 10000` was directionally useful but methodologically blunt: it correctly showed that the shortlist had stabilized, yet it overshot the exact stabilization threshold by a factor of `10`.

This matters because below cap `10` the hazard guardrail is not “inactive.” It is actively collapsing the shortlist and silently removing the lower-delta material-first anchor. Only once the cap reaches `10` does the hazard dimension stop doing substantive selection inside the already-derived family10 width/ceiling plateau box.

That means the inheritor should now publish one compact contract instead of three disconnected facts:

1. family `10/20/50/100`,
2. width floor anywhere in `0.00026 < floor <= 0.00129`,
3. hazard cap `>= 10`,
4. delta ceiling anywhere in `0.00822 < ceiling <= 0.01944`.

Anywhere inside that box, the shortlist and the declared priority winners are unchanged.

The implementation consequence is small but important: hazard reporting should expose the **first clearing cap** for each candidate and the **first cap at which the full intended shortlist appears**, not just a handful of arbitrary larger caps. That turns the guardrail from a ceremonial methods parameter into a reproducible policy boundary.
