# Specialisations and variants (within a generation)

NixOS has a useful concept called **specialisations**: within a single system generation, you can define *variations* and switch between them (sometimes at boot-time, sometimes at runtime).

DeriveBSD should adopt this idea in a way that fits our model:

* host bytes remain immutable and signed
* variants are explicit, policy-governed, and explainable

## Why DeriveBSD wants this

* **Safe-mode**: a “minimal networking” or “no third-party drivers” variant is a lifesaver.
* **Role variants**: same base generation, different enabled workload bundles.
* **Debug variants**: attach a system extension, enable extra logging, without rebuilding the base.

## Model

### Variant is a derived artifact

Within a given generation `G`, define named variants `V`:

* `variant.plan_digest = H(G.plan_digest || variant_spec_digest || policy_decision_digest)`
* the variant produces a `variant.activation` bundle (svcdb targets, pf anchors, mounts/extensions)

Variants must not change the immutable store closure of `G` unless that change is expressed as a separate derived artifact (e.g., system extension image).

### Switching

* `derive variant list`
* `derive variant switch <name>`
* `derive variant boot <name>` (set next-boot variant)

The switch action emits evidence:

* `variant.switch.receipt`
* `variant.previous` / `variant.next`

## Guardrails

* variants are **declared** and **bounded** (no arbitrary scripting)
* policy can forbid variants that relax security posture (or require explicit override)
* variants are diffable (“what changed?”)

## References

* NixOS specialisations overview.
