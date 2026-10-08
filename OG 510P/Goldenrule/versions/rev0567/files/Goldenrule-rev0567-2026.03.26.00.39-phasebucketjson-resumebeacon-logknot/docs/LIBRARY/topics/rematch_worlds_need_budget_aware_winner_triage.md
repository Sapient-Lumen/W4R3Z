# Rematch worlds need budget-aware winner triage

Winner certification is not the end of the rematch reporting contract.

The new derived report in `artifacts/reports/rematch_proxy_certification_budget_snapshot_20260306.{md,json}` asks the next implementor-facing question: when a top panel is still uncertified, how expensive would it be to certify the current point-estimate leader if the observed effect size and paired variance persist?

That matters because the archive is supposed to stay compact. In the current proxy, the only uncertified top panel would need an estimated `425` paired seeds total to certify its current point-estimate winner under a simple fixed-precision planning proxy, versus the current `6`. That is a strong sign that some unresolved flips are not good default targets for brute-force reruns.

So the reporting contract should get one step sharper:

- publish winner certification status,
- publish an approximate additional-budget-to-certify field for unresolved top panels,
- and allow a budget-aware near-tie / indifference label when certification would require orders of magnitude more simulation than the baseline budget.

This keeps the archive small and decision-focused. Instead of growing a bulky trail of increasingly expensive reruns to separate microscopic effects, the inheritor gets a compact triage artifact: certify now, defer, or record a frontier tie.

The budget estimate is not itself a proof. It is a planning proxy and should be recomputed whenever the world semantics, policy set, noise model, or random-stream coupling changes. But even a rough estimate is enough to stop the archive from mistaking tiny unresolved flips for mandatory simulation work.
