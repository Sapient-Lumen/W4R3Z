# Regularization / renormalization / matching discipline

## Purpose

This surface owns `OQ-0076`. It prevents a route from treating a regulator-specific calculation, subtraction convention, cutoff choice, RG trajectory, running coupling, fixed-point coordinate, threshold match, EFT match, counterterm choice, or naturalness story as candidate-native support unless the relevant scheme, flow, and matching rows are declared.

The archive distinction is:

```text
regulated calculation
  -> renormalized or coarse-grained description
  -> matched physical / public-record invariant
  -> route-local authority effect
```

A route may not skip the middle two arrows.

## Executable ledgers

- `REGULARIZATION-SCHEME-LEDGER.json` names the regulator, cutoff, subtraction prescription, basis, simulator filter, survey/pipeline parameterization, or package-only wrapper.
- `RENORMALIZATION-FLOW-LEDGER.json` names the RG/coarse-graining trajectory, scale parameter, running object, fixed-point or universality claim, and residual scheme/truncation debt.
- `MATCHING-CONDITION-LEDGER.json` names the source theory or scale, target theory or public record, matching object, threshold/power-counting rule, unmatched residual, and forbidden inference.

The generated program mirror is `docs/30-program/renormalization-matching-summary.generated.md`.

## Stop rule

No route may use this language without current rows in all three ledgers:

```text
regularized
renormalized
scheme-independent
RG-invariant
fixed point
critical surface
running coupling
beta function
counterterm
threshold matched
EFT matched
Wilson coefficient
naturalness
universality class
UV completion
scale bridged
```

## Non-promotion rule

Regularization, renormalization, and matching rows can cap, freeze, repair, or roll back route language. They cannot promote a route beyond its state-machine ceiling. A scheme-independent physical observable still needs public-record, observed-sector, measurement, validity, causal, selection, capacity, semantic, social, computational, formal-proof, idealization, boundary, gauge, and residual-cap support before stronger wording is allowed.

## Route-local questions

Each route must answer:

```text
What is the regulator or subtraction scheme?
What coordinate, coupling, or parameter is scheme-dependent?
Which object is claimed to be invariant?
What scale is physical, cutoff, renormalization, radial, detector, survey, or package-only?
What is running: a coordinate, a coupling, a Wilson coefficient, a likelihood parameter, or a public observable?
What matching object transfers support from source to target?
What residual is unmatched?
Which rollback fires if the result is scheme-specific?
```

## Metadata demotion

Archive manifests, generated summaries, version tags, and package provenance can improve custody. They do not supply a physical regulator, RG flow, counterterm, fixed point, Wilson coefficient, matching condition, scheme-independence test, or universal quantity.
