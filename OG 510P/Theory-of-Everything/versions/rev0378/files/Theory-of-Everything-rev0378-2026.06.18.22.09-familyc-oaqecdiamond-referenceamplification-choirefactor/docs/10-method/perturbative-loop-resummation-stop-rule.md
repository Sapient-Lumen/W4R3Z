# Perturbative / loop / resummation stop rule

`OQ-0105` blocks perturbative, loop-order, counterterm, all-order, Borel, resurgence, renormalon, transseries, and resummation language unless three route-local rows are current:

1. `PERTURBATIVE-EXPANSION-LEDGER.json`
2. `LOOP-ORDER-COUNTERTERM-LEDGER.json`
3. `RESUMMATION-BOREL-LEDGER.json`

A route may not infer all-order consistency from one finite order, nonperturbative completion from resummation, or candidate identity from an EFT corridor. Failures roll back to the route ceiling declared in the candidate route ledger.
