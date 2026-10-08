# Systematic uncertainty and calibration traceability

Revision: `rev0267`
Owner ledgers: `SYSTEMATIC-UNCERTAINTY-LEDGER.json`, `CALIBRATION-TRACEABILITY-LEDGER.json`
Open question: `OQ-0064`

The archive now treats systematic uncertainty and calibration traceability as executable authority constraints. A likelihood/update row is only as strong as the measurement chain, correction model, nuisance stack, and traceability lineage that produced it.

For physical measurements this imports ordinary metrology discipline: measurand, calibration, uncertainty, reference standard, traceability, drift, and correction chains. For computational and formal routes, the analogous chain is verification/validation, benchmark provenance, proof environment, truncation/regulator specification, input-data versioning, and replayable audit artifact.

Every systematic row asks:

```text
What could bias the route-local observable?
Which nuisance parameters or model choices carry that bias?
What stress test would expose it?
What mitigation or bound exists?
What residual effect remains after mitigation?
Which rollback rule fires if the budget fails?
```

Every calibration/traceability row asks:

```text
What is the reference object or standard?
What is the calibration/proof/benchmark/data-release chain?
How is uncertainty propagated into the update row?
How is drift controlled?
What replay or audit artifact proves the chain?
What happens if traceability breaks?
```

No route may compensate for a broken measurement chain using formal beauty, public metadata, many citations, favorable likelihood ratios, or broad candidate plausibility.
