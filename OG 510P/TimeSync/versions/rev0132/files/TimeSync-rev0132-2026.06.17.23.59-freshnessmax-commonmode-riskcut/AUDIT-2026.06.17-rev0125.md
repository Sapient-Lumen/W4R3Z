# TimeSync rev0125 audit — policyacceptance-boundaryrefactor-riskcut

## Risk selected

The riskiest incomplete area after rev0124 was not another registry or schema. It was profile-decision drift: the adapter path could compute and independently recompute a chrony-derived TimeState, but the P1 lane thresholds still lived as duplicated Python literals.

If those thresholds drifted or if an exact-boundary comparison changed from inclusive to exclusive, TimeSync could either over-authorize stale time or unnecessarily reject usable time. That is a real operational risk and a better target than adding another doctrine file.

## Changes made

- Added `evaluator/p1-chrony-policy.json` as the machine-readable P1 chrony policy artifact.
- Added `tools/chrony_policy.py` to validate the policy artifact and apply inclusive lane decisions.
- Refactored `tools/chrony_adapter.py` and `tools/chrony_observation_eval.py` so threshold values and policy-reference text are not duplicated literals.
- Added `tests/profile-decision-acceptance.yaml` and `tools/profile_decision_acceptance.py` to run exact and one-nanosecond-after boundary cases through the primary adapter and independent evaluator.
- Added generated example `examples/evaluator/chrony-p1-after-display-limit-unsatisfied.json` and semantic vector `TV-125-001`.

## Audit/refactor result

The key refactor is deliberately small: `chrony_policy.py` owns only the lane table and decision application. It does not parse chrony, compute error bounds, produce TimeState, or verify authentication. This keeps the narrow waist intact and avoids turning policy extraction into another ontology.

The old documentary acceptance list remains documentary. rev0125 adds an executable acceptance layer for the live vertical slice rather than pretending all 124 prose scenarios are runnable.

## Severe/wasteful issue corrected

Repeated hidden threshold literals were a wasteful and risky source of false assurance. They made it easy for the primary and independent evaluator to stay textually similar while still lacking a first-class policy artifact. Rev0125 corrects that by making the policy table auditable and by testing the boundary crossings that would matter in operation.

## Still open

- The live path is implemented but not exercised in this cloud container because `chronyc` is not installed.
- NTS and symmetric-key authentication are not verified.
- UTC is chrony-reported and unqualified; named UTC realization is not proven.
- Leap-smear policy discovery is not implemented.
- RFC 9249 remains a comparison guard, not proof of interoperability.
- The machine-readable policy covers only P1 chrony reference evaluation.
