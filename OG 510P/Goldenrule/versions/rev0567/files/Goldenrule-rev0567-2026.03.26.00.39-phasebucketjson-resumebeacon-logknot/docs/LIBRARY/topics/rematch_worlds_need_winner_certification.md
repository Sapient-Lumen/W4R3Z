# Rematch worlds need winner certification

A rematch leaderboard should not stop at a point-estimate winner.

The new derived report in `artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.{md,json}` asks a deliberately narrow question: once the current proxy's raw leader and runner-up are compared seed-by-seed, which tested panels still have a winner whose top-vs-runner-up margin is clearly above zero?

That matters because simulation ranking is a statistical selection problem, not just a sorting problem. In the current proxy, the only tested raw leader flip is also the only uncertified panel under a paired 95% interval rule. So promoting that flip into a stable archive claim would be premature.

The implementor-facing contract is therefore tighter than “publish leader margins”:

- publish the tested-band winner and runner-up,
- publish the paired-seed top-gap uncertainty field (or an equivalent PCS-style certification flag),
- and treat winner flips that do not clear that gate as provisional frontier uncertainty rather than clean strategy reversals.

This keeps the archive compact. Instead of storing many bulky sweep tables or arguing over tiny point-estimate flips, the inheritor gets a small decision artifact: certified winners, uncertified panels, and the uncertainty gate that separates them.

The contract should stay paired where possible. If benchmark policies share seeds or random streams, the top-gap should use that matched structure rather than a looser independent-sample estimate. Any major change to noise semantics, entrant pool, delay band, or persistence rules should trigger a fresh winner-certification pass.
