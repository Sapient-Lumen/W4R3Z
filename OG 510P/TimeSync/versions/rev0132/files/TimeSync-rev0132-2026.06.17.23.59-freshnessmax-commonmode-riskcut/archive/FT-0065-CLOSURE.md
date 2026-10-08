# FT-0065 closure — timescale realization and clock continuity

FT-0065 asked whether TimeSync needs compact hooks for UTC realization, leap/smear behavior, backward-step policy, and monotonicity pressure without expanding the six-field TimeState core.

rev0066 closes the ticket with two extension hooks:

```text
extension_hooks.timescale_realization
extension_hooks.clock_continuity_posture
```

## Decision

Add the hooks, but keep them outside TimeState.

The TimeState core still contains only:

```text
interval
timescale
freshness
regime
source_posture
applicability
```

The new hooks are profile-facing semantic inputs. They do not define a time protocol, clock discipline algorithm, leap-second procedure, source-selection model, or provenance graph.

## Why the hook is necessary

A core claim such as `timescale: UTC` does not by itself state:

- whether UTC is a named realization,
- whether a provider applies a smear,
- whether a future UTC continuity transition is being handled by local policy,
- whether local time can step backward,
- or whether monotonic local ordering has been claimed or assessed.

Those questions affect profile applicability in finance, telecom, critical infrastructure, degraded continuity, and distributed coordination.

## Implemented artifacts

- `spec/29-timescale-realization-and-clock-continuity.md`
- `schema/extension-hooks.schema.json`
- `schema/local-assessed-state.schema.json`
- Updated P1-P6 profile obligations and profile digests
- `examples/p2-coordination-smeared-continuity.json`
- Negative fixtures for contradiction and malformed discovery returns
- Validator rules for realization/continuity consistency

## Explicit non-goals

The closure does not standardize:

- a smear algorithm,
- NTP/PTP management behavior,
- grandmaster election,
- oscillator modeling,
- source diversity,
- or legal proof of traceability.

The next open frontier is source-diversity/common-mode dependency posture without exporting a source roster.
