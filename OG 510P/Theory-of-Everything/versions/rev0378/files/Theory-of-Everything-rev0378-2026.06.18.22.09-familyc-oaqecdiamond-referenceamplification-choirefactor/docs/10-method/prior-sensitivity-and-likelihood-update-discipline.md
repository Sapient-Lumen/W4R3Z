# Prior-sensitivity and likelihood-update discipline

This surface treats priors, nuisance stacks, model-class weights, quotient choices, simulator targets, and benchmark definitions as first-class update controls.

## Rule

A public likelihood, benchmark score, proof survival, reconstruction result, catalog analysis, or observational fit is not archive-level support until the route says how the result changes under plausible changes to:

- prior family or parameter bounds,
- nuisance model,
- gauge / frame / quotient convention,
- regulator or truncation basis,
- detector / source-state model,
- survey covariance or foreground model,
- simulator target and train/test split,
- contrast-class composition.

## Update ceiling

Prior sensitivity is conservative. It may:

```text
cap support
merge support
split support
block update language
trigger rollback
```

It may not:

```text
promote a route
turn a forecast into a result
turn a likelihood into ontology
turn metadata into physical evidence
turn correlated support into independent convergence
```

## Local use

Use this file whenever a route tries to say:

- “the data favor candidate X,”
- “the benchmark supports candidate X,”
- “the likelihood prefers this model,”
- “the positive result confirms the route,”
- “the null result supports the baseline,”
- “the public catalog makes the case stronger.”

The correct next question is: stronger against which alternatives, under which priors, through which likelihood/update object, and with what ceiling?

## Executable surfaces

- `LIKELIHOOD-UPDATE-LEDGER.json`
- `PRIOR-SENSITIVITY-LEDGER.json`
- `CONTRAST-CLASS-LEDGER.json`
- `EVIDENCE-UNIT-LEDGER.json`
- `CREDIT-ALLOCATION-LEDGER.json`
