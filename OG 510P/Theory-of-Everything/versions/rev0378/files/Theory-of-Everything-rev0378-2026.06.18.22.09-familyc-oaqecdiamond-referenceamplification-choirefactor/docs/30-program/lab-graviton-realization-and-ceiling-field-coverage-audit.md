# Lab graviton realization and ceiling-field coverage audit (rev0333)

## Risk corrected

Two distinct authority leaks were still open after the route-source staging work.

First, the route-condition ceiling policy covered the common S-level fields (`maximum_authority_effect`, `maximum_credit`, `current_maximum_credit`, and `promotion_ceiling`), but several spendable authority fields were outside the evaluator: carrier `maximum_authority_credit`, protocol `maximum_route_effect`, severity `maximum_credit_if_passed`, ontology `realist_status_ceiling`, and contrast-class `current_update_ceiling`. Those fields are not harmless metadata. They are exactly where a public-record carrier, acquisition protocol, contrast class, or severity row can launder more authority than a route should be allowed to spend.

Second, the realization-status audit protected the lab GIE/BMV route, but not the lab graviton-counting route. That left a conditional-S3 lab route whose present support is proposal/theory pressure at current S2, while a future detector-local click/count/statistics record was still easy to read as already realized.

## Change made

`tools/route_condition_ceiling_policy.py` now treats the following fields as S-level authority fields whenever they appear in JSON rows:

- `maximum_authority_effect`
- `maximum_credit`
- `current_maximum_credit`
- `promotion_ceiling`
- `maximum_authority_credit`
- `maximum_route_effect`
- `maximum_credit_if_passed`
- `realist_status_ceiling`
- `current_update_ceiling`

Adding those fields exposed thirteen multi-route rows that carried S-level credit but lacked explicit route-spendable caps. rev0333 adds `route_authority_ceilings` to those carrier, protocol, severity, and contrast rows. The cap rule is conservative: the route-spendable cap may not exceed either the row envelope or the route's own promotion ceiling.

`tools/route_realization_policy.py` now checks both conditional lab routes:

- `R-OQ0057-LAB-GIE-BMV`
- `R-OQ0057-LAB-GRAVITON-COUNTING`

For the graviton-counting route, it requires current S2 / conditional S3 posture, forecast-public evidence status, detector-local source refs, the realization delta, decision hooks, trigger/source-state/background/calibration artifacts, and explicit claim-language prohibitions against treating a proposal or a classical GW trigger catalog as detector-local single-graviton evidence.

## Substantive interpretation

The single-graviton lane remains live because recent quantum-sensing and graviton-counting/statistics proposals are no longer mere impossibility folklore. However, present support is still source-theory/proposal pressure until a detector-local public record exists. A classical gravitational-wave trigger can supply timing/source covariance; it is not itself a quantum click, state-tomography artifact, or candidate-native observable.

The route therefore remains current `S2` with only a bounded conditional `S3` pocket for a future acquired public record that survives detector response, background rejection, source-state ambiguity, trigger selection, calibration lineage, replay, and non-ontology controls.

## Audit-bloat refactor

The route-condition ceiling audit previously retained thousands of PASS rows and was mostly control-plane exhaust. The evaluator still checks every row and field, but the generated audit now retains compact route/field/file summaries plus failures. The retained generated file drops from roughly 554 KB in rev0332 to roughly 11 KB in rev0333.

## Release hot-path refactor

While validating the package, the smoke wrapper reproduced a cloudtainer-specific parent/child polling hang: extracted `lint_archive.py` printed `LINT OK`, but the heartbeat parent could keep polling instead of advancing to schema validation. rev0333 replaces that inherited-output polling path with bounded captured subprocess output. The extracted smoke contract is unchanged: clean, lint, registered JSON Schema validation, deterministic rebuild, and byte-identical SHA comparison still have to pass. The change removes release-harness waste rather than weakening package validation.

## Non-promotion rule

No route is promoted. The changes close authority-field coverage holes, add missing conditional-record checks for the lab graviton-counting route, and reduce retained audit exhaust. They do not add a detector-local single-graviton record, a GIE/BMV public run, a unique quantization proof, or Theory-of-Everything identity support.
