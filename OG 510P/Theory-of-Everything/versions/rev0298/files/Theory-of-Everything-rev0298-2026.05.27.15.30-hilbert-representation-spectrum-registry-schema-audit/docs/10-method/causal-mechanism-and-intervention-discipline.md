# Causal mechanism and intervention discipline

Revision: `rev0269`

This surface owns the causal/mechanistic denominator added in rev0269.

The archive may have a public record, a valid-domain row, a transport map, a calibrated observable, a likelihood update, and a severe test. That still does not license causal language by itself. A route can say that a record is mechanistic, causal, mediator-confirming, intervention-backed, or natural-experiment-relevant only when the executable causal rows say what kind of causal object is being claimed.

## Rule

```text
fit / reconstruction / likelihood / constraint / forecast
≠ causal mechanism
≠ intervention support
≠ mediator ontology
≠ counterfactual robustness
```

The minimum denominator is:

```text
causal question
+ proposed mechanism or graph/structure
+ causal claim grain
+ manipulability or unmanipulability gap
+ confounding/common-cause controls
+ intervention, perturbation, ablation, or natural-experiment status
+ invariance or mechanism-stability test
+ maximum authority effect
+ rollback handle
```

## Executable surfaces

- `CAUSAL-MECHANISM-LEDGER.json` names the candidate-local causal question, proposed structure, common-cause/confounding controls, mechanism-stability test, and maximum authority effect.
- `INTERVENTION-PROTOCOL-LEDGER.json` separates direct interventions, indirect perturbations, formal variations, simulation ablations, natural experiments, unmanipulable observations, and custody-only edits.
- `COUNTERFACTUAL-ROBUSTNESS-LEDGER.json` names the counterfactual query, allowed alternative worlds or model interventions, invariance requirement, failure modes, and rollback effect.

## Non-promotion rule

These rows are gates and caps. They never promote a route. They only prevent a route from spending mechanism, cause, mediator, intervention, natural-experiment, ablation, or counterfactual language when the denominator is missing.

## Gravity-specific caution

Many route records are observational, formal, or reconstruction-based rather than manipulable. That is allowed. The row may say `unmanipulable-observational`, `formal-variation`, or `counterfactual-only`. But then the route must not borrow direct-intervention language.

## Metadata caution

Metadata, provenance, generated summaries, and package identity improve custody and replay. They are nonmechanisms. The metadata causal rows exist solely to block metadata-as-causal-evidence laundering.
