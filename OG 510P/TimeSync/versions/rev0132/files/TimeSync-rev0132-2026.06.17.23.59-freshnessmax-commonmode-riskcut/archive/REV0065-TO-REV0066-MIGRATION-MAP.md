# Migration map — rev0065 to rev0066

## Summary

rev0066 adds timescale realization and clock-continuity posture as extension hooks. It does not alter the TimeState core.

## Mechanical changes

Add support for two new optional extension hooks:

```text
extension_hooks.timescale_realization
extension_hooks.clock_continuity_posture
```

Update schema consumers that embedded `extension-hooks.schema.json` or `local-assessed-state.schema.json`.

## Profile obligation changes

| Profile | Change |
|---|---|
| P1 | `timescale_realization` and `clock_continuity_posture` are requestable. |
| P2 | `timescale_realization` and `clock_continuity_posture` are requestable. |
| P3 | `timescale_realization` is profile-default; `clock_continuity_posture` is requestable. |
| P4 | both hooks are requestable. |
| P5 | both hooks are profile-default. |
| P6 | `clock_continuity_posture` is profile-default; `timescale_realization` is requestable. |

Because obligation placement is normative, all profile digests changed.

## Evidence-summary changes

Profiles that include a new hook as a profile-default or minimum evidence item must include the corresponding item name in retained/requested evidence summaries, for example:

```text
extension_hooks.timescale_realization
extension_hooks.clock_continuity_posture
```

P3 retained evidence summaries now include `extension_hooks.timescale_realization`.

## Validator changes

rev0066 rejects:

- a specific `timescale_realization.scale` that contradicts `timestate.timescale`,
- `traceability_posture.reference_anchor: utc_named_realization` without a named realization,
- a smeared realization paired with `smear_policy: none` or `not_applicable`,
- malformed returned hook values in discovery results,
- unknown profile obligation item names,
- and unknown evidence-policy minimum item names.

## Compatibility guidance

A rev0065 consumer that ignores unknown extension hooks can still read the six-field TimeState core, but it cannot claim rev0066 profile conformance for profiles whose new profile-default obligations are required.

A rev0066 producer should not place realization or continuity details inside `timestate.timescale`, `freshness`, or `source_posture`. Use the new hooks.
