# 29 — Timescale realization and clock-continuity hooks

rev0066 closes FT-0065 by adding two compact extension hooks:

```text
extension_hooks.timescale_realization
extension_hooks.clock_continuity_posture
```

They do not alter the six-field TimeState core. rev0067 leaves these hooks unchanged and adds source-diversity posture separately in `spec/30-source-diversity-and-common-mode-posture.md`.

## Why this exists

The `timestate.timescale` field intentionally stays small. `UTC` is a useful semantic claim, but it is not always enough for profile evaluation. Some domains need to know whether UTC is unqualified, a named realization such as a national laboratory realization, a smeared provider time, a profile-defined realization, or a local private continuity scale.

The same interval can be acceptable for one profile and unacceptable for another if leap handling, smear behavior, backward-step policy, or local monotonicity assumptions differ.

The hook exists because those details are profile-facing semantic inputs. They are not a clock-servo model, source path, grandmaster-selection algorithm, or timing protocol.

## timescale_realization

Shape:

```text
timescale_realization:
  scale: UTC | TAI | GPS | local_private | profile_defined | unknown
  realization: string
  leap_handling: standard_utc | smeared | continuous_utc_transition | not_applicable | unknown
  tai_utc_offset_state: known | unknown | not_applicable
  evidence_posture: claimed | traceable | profile_defined | not_applicable | unknown
```

Rules:

- `timestate.timescale` remains the compact core claim.
- `timescale_realization.scale` must not contradict `timestate.timescale` when both are specific.
- `traceability_posture.reference_anchor: utc_named_realization` requires a real `timescale_realization` object with `scale: UTC` and a non-generic realization name.
- A named UTC realization can be traceable, claimed, profile-defined, or unknown; profile rules decide what is enough.
- `leap_handling: smeared` says the exported interval is in a smeared representation, not step UTC.
- `leap_handling: continuous_utc_transition` is reserved for future UTC continuity transition policy. It is not a promise that TimeSync understands the full future UTC definition.

## clock_continuity_posture

Shape:

```text
clock_continuity_posture:
  backward_step_policy: forbidden | bounded | permitted | unknown
  smear_policy: none | leap_smear | policy_defined | not_applicable | unknown
  monotonic_local_time: claimed | assessed | not_claimed | unknown
  evidence_posture: claimed | assessed | profile_defined | not_applicable | unknown
```

Rules:

- This hook summarizes continuity assumptions relevant to profile evaluation.
- It does not expose the local clock algorithm.
- `smear_policy` must agree with `timescale_realization.leap_handling` when both are present.
- `monotonic_local_time` is a semantic posture, not an exported monotonic-clock reading.

## Profile placement

rev0066 introduced the profile obligations as follows:

- P1 and P2 may request both hooks.
- P3 treats `timescale_realization` as profile-default evidence for traceable finance and may request `clock_continuity_posture`.
- P4 may request both hooks because telecom frequency/phase/time cases differ by deployment.
- P5 treats both hooks as profile-default evidence for critical-infrastructure precision.
- P6 treats `clock_continuity_posture` as profile-default evidence for local degraded continuity and may request `timescale_realization`.

## Discovery

Discovery may return either hook as an ordinary flat result item. Returned values are schema-validated. Negative result statuses remain `unavailable`, `unknown`, and `omitted`.

There is still no negotiation, bundle lifecycle, or source roster.

## Evidence summaries

If a profile declares these hooks as profile-default or minimum evidence-summary items, evaluator summaries must include them by item name, for example:

```text
extension_hooks.timescale_realization
extension_hooks.clock_continuity_posture
```

The summary records item presence, evidence class, and obligation result. It does not export the underlying source list, time samples, clock algorithm, or external audit path.

## Non-goals

These hooks do not standardize:

- leap-second insertion procedures,
- NTP/PTP behavior,
- a smear algorithm,
- source selection,
- grandmaster election,
- oscillator holdover modeling,
- path delay measurement,
- or legal traceability evidence.

Those remain carrier, profile, local-policy, or external-audit matters.
