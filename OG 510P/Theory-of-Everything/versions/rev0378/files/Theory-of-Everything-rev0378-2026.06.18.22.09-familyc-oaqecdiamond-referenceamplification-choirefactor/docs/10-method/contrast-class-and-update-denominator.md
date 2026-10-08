# Contrast-class and update denominator

This surface owns the `OQ-0063` rule that evidence must be contrastive before it can be spent as route support.

A route-local support packet is not just:

```text
record exists -> candidate supported
```

It must instead carry at least:

```text
record object
+ contrast class
+ rival / null / decoy family
+ quotient policy
+ likelihood or benchmark update object
+ nuisance and prior sensitivity controls
+ maximum authority effect
```

## Why this exists

The earlier executable layers already block several overclaims: unowned route states, public-record handwaving, missing acquisition protocols, silent rollback, and double-counted evidence. The remaining weakness was contrast leakage. A record could still be described as supporting a route without saying what it supports the route *against*.

This file fixes that by making support contrastive. Evidence may constrain a family, distinguish a model class, improve a benchmark, or reduce a parameter region without identifying a candidate ontology. The contrast denominator decides which of those happened.

## Required distinction

| Object | Question | Authority effect |
|---|---|---:|
| Contrast class | Against which live alternatives is this evidence being read? | caps candidate / family / parameter wording |
| Likelihood/update row | What score, likelihood, proof-survival predicate, benchmark result, or qualitative update changed? | local route update only |
| Prior-sensitivity row | Which priors, nuisance assumptions, quotient choices, or model-class weights change the result? | cap, merge, or rollback support |
| Evidence unit | Which support packet is being counted? | prevents double-counting |
| Credit allocation | How may this packet aggregate with others? | no-compensation accounting |

## Non-promotion rule

A contrast class can lower, split, or localize support. It cannot promote a route by itself. A route-state change still requires the candidate-identifiability state machine, promotion gates, observed-sector obligations, public-record carriers, acquisition protocols, negative controls, defeater / rollback rows, severity tests, evidence-unit accounting, independence assumptions, credit allocation, and residual caps.

## Forbidden moves

- Treating a likelihood ratio, Bayes factor, benchmark score, theorem, catalog, or forecast as support without naming the rival set.
- Treating a null result as broad support without naming which alternatives were actually at risk.
- Treating a positive result as candidate-native support when the contrast was only family-level, parameter-level, or artifact-level.
- Treating metadata, repository presence, generated summaries, or package identity as physical support.
- Transferring confirmation from a large package to one candidate part without declaring the transfer rule.

## Executable surfaces

- `CONTRAST-CLASS-LEDGER.json`
- `LIKELIHOOD-UPDATE-LEDGER.json`
- `PRIOR-SENSITIVITY-LEDGER.json`
- `docs/30-program/contrast-update-summary.generated.md`
