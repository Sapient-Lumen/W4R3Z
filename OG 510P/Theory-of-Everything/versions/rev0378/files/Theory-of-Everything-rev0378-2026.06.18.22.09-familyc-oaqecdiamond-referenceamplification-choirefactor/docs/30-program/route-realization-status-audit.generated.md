# Route realization-status audit (generated)

Generated from route, evidence, empirical-delta, decision, severity, claim-language, and lab-control ledgers. Do not edit directly; run `make index` after changing realization-sensitive rows.

- Conditional lab routes checked: `2`
- Realization-status checks: `54`
- Realization-status failures: `0`

| Route | Current state | Conditional ceiling | Evidence status | Evidence credit | Checks | Failures |
|---|---:|---:|---|---:|---:|---:|
| `R-OQ0057-LAB-GIE-BMV` | `S2` | `S3` | `forecast-public-record` | `S2` | `24` | `0` |
| `R-OQ0057-LAB-GRAVITON-COUNTING` | `S2` | `S3` | `forecast-public-record` | `S2` | `30` | `0` |

## R-OQ0057-LAB-GIE-BMV

- Evidence unit: `EU-0008-LAB-GIE-MEDIATOR`
- Realization delta: `ED-0017-GIE-BMV-INFERENCE-SPLIT-PRESSURE`
- Required current source refs: `REF-0643`, `REF-0644`, `REF-0645`, `REF-0646`

| Check | Passed | Detail |
|---|---:|---|
| `route-present` | `true` | missing route `R-OQ0057-LAB-GIE-BMV` |
| `evidence-present` | `true` | missing evidence unit `EU-0008-LAB-GIE-MEDIATOR` |
| `realization-delta-present` | `true` | missing empirical delta `ED-0017-GIE-BMV-INFERENCE-SPLIT-PRESSURE` |
| `decision-present` | `true` | missing decision row `DX-0001-DIRECT-GIE-BMV-ENTANGLEMENT` |
| `severity-present` | `true` | missing severity row `SV-0003-DIRECT-GIE-BMV-SEVERITY` |
| `language-present` | `true` | missing claim-language row `LPP-0008-LAB-GIE-BMV` |
| `current-state-is-bounded` | `true` | authority_state is `S2` |
| `conditional-ceiling-is-declared` | `true` | promotion_ceiling is `S3` |
| `route-residual-names-missing-record` | `true` | residual_cap must contain ['direct', 'public'] |
| `evidence-is-forecast-public` | `true` | record_status is `forecast-public-record` |
| `evidence-current-credit-is-bounded` | `true` | maximum_credit is `S2` |
| `evidence-carries-current-realization-refs` | `true` | missing refs [] |
| `evidence-links-realization-delta` | `true` | ED-0017-GIE-BMV-INFERENCE-SPLIT-PRESSURE missing from evidence empirical_delta_ids |
| `delta-route-bound` | `true` | R-OQ0057-LAB-GIE-BMV missing from delta route_ids |
| `delta-carries-current-realization-refs` | `true` | missing refs [] |
| `delta-ceiling-is-conditional` | `true` | promotion_ceiling is `S3` |
| `delta-state-effect-caps-current-credit` | `true` | state_effect must cap current credit and name conditional future record |
| `decision-carries-current-realization-refs` | `true` | missing refs [] |
| `decision-links-realization-delta` | `true` | ED-0017-GIE-BMV-INFERENCE-SPLIT-PRESSURE missing from decision empirical_delta_hooks |
| `decision-minimum-artifact-is-detector-local` | `true` | minimum_public_artifact must contain ['calibrated', 'controls'] |
| `clean-outcome-is-conditional` | `true` | clean outcome must contain ['conditional', 'direct', 'public'] |
| `severity-carries-current-realization-refs` | `true` | missing refs [] |
| `language-carries-current-realization-refs` | `true` | missing refs [] |
| `language-forbids-proposal-as-proof` | `true` | forbidden_language must contain ['entanglement by itself'] |

## R-OQ0057-LAB-GRAVITON-COUNTING

- Evidence unit: `EU-0011-GRAVITON-COUNTING`
- Realization delta: `ED-0018-GRAVITON-REALIZATION-AND-QUANTIZATION-SPLIT-PRESSURE`
- Required current source refs: `REF-0175`, `REF-0176`, `REF-0647`, `REF-0648`

| Check | Passed | Detail |
|---|---:|---|
| `route-present` | `true` | missing route `R-OQ0057-LAB-GRAVITON-COUNTING` |
| `evidence-present` | `true` | missing evidence unit `EU-0011-GRAVITON-COUNTING` |
| `realization-delta-present` | `true` | missing empirical delta `ED-0018-GRAVITON-REALIZATION-AND-QUANTIZATION-SPLIT-PRESSURE` |
| `decision-present` | `true` | missing decision row `DX-0013-GRAVITON-COUNTING-STATE-STATISTICS-CORRIDOR` |
| `severity-present` | `true` | missing severity row `SV-0004-GRAVITON-COUNTING-SEVERITY` |
| `language-present` | `true` | missing claim-language row `LPP-0011-LAB-GRAVITON-COUNTING` |
| `current-state-is-bounded` | `true` | authority_state is `S2` |
| `conditional-ceiling-is-declared` | `true` | promotion_ceiling is `S3` |
| `route-residual-names-missing-record` | `true` | residual_cap must contain ['realized public', 'no S4/S5'] |
| `evidence-is-forecast-public` | `true` | record_status is `forecast-public-record` |
| `evidence-current-credit-is-bounded` | `true` | maximum_credit is `S2` |
| `evidence-carries-current-realization-refs` | `true` | missing refs [] |
| `evidence-links-realization-delta` | `true` | ED-0018-GRAVITON-REALIZATION-AND-QUANTIZATION-SPLIT-PRESSURE missing from evidence empirical_delta_ids |
| `delta-route-bound` | `true` | R-OQ0057-LAB-GRAVITON-COUNTING missing from delta route_ids |
| `delta-carries-current-realization-refs` | `true` | missing refs [] |
| `delta-ceiling-is-conditional` | `true` | promotion_ceiling is `S3` |
| `delta-state-effect-caps-current-credit` | `true` | state_effect must cap current credit and name conditional future record |
| `decision-carries-current-realization-refs` | `true` | missing refs [] |
| `decision-links-realization-delta` | `true` | ED-0018-GRAVITON-REALIZATION-AND-QUANTIZATION-SPLIT-PRESSURE missing from decision empirical_delta_hooks |
| `decision-minimum-artifact-is-detector-local` | `true` | minimum_public_artifact must contain ['trigger', 'calibration', 'background', 'source-state', 'detector-local'] |
| `clean-outcome-is-conditional` | `true` | clean outcome must contain ['conditional', 'S3', 'not full ToE'] |
| `severity-carries-current-realization-refs` | `true` | missing refs [] |
| `language-carries-current-realization-refs` | `true` | missing refs [] |
| `language-forbids-proposal-as-proof` | `true` | forbidden_language must contain ['single-graviton proposal proves quantization', 'classical GW trigger catalog'] |
| `protocol-row-present` | `true` | missing protocol row `AP-SINGLE-GRAVITON-TRIGGER-CORRELATION` |
| `protocol-carries-current-realization-refs` | `true` | missing refs [] |
| `measurement-row-present` | `true` | missing measurement row `MM-0011-LAB-GRAVITON-COUNTING` |
| `measurement-carries-current-realization-refs` | `true` | missing refs [] |
| `calibration-row-present` | `true` | missing calibration row `CAL-0011-LAB-GRAVITON-COUNTING` |
| `calibration-carries-current-realization-refs` | `true` | missing refs [] |

## Rule

A route whose direct detector-local public record is still unrealized may keep a conditional ceiling for a future clean record, but its current authority state and evidence unit must not spend that future result. For the lab GIE/BMV and lab graviton-counting lanes, current support remains proposal/review/feasibility/inference pressure (`S2`) until a direct acquired public record survives nuisance, subsystem, trigger, source-state, background, calibration, classical/hybrid, and model-class controls. This audit creates no support and promotes no route.

