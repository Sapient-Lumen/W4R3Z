# TimeSync rev0127 audit — captureinstant-ageguard-riskcut

## Risk selected

The riskiest remaining executable seam after rev0126 was not another chrony command role. It was the exact instant used to age replayed evidence.

The capture envelope correctly bracketed the whole collector run, but replay extraction used the collector's final wall timestamp as `collected_at`. That is too optimistic whenever `chronyc -n tracking` runs before later commands such as `sources` or `sourcestats`. Since the evaluator grows the interval by `skew_ppm * age`, a later collector timestamp can understate holdover age and silently narrow the interval.

## Changes made

- Added `effective_tracking_collected_at(...)` in `tools/chrony_capture.py`.
- Changed `extract_replay_inputs(...)` to use the start of the `tracking` command as the conservative replay `collected_at`.
- Preserved the collector final wall timestamp separately as `capture_context.collector_collected_at`.
- Added `capture_context.effective_collected_at_basis = tracking_command_start_wall_conservative` and retained tracking command start/end/duration context.
- Added delayed-command fixture `tests/fixtures/chrony/capture-delayed-tracking.json`.
- Added `CHRONY-P1-CAPTURE-TRACKING-INSTANT-AGE-GUARD` to prove a capture whose collector finishes ten seconds later still ages from the tracking command instant.
- Added generated example `examples/evaluator/chrony-p1-capture-instant-ageguard-satisfied.json` and semantic vector `TV-127-001`.

## Audit/refactor result

The capture boundary now distinguishes three instants instead of overloading one field:

- collector wall bracket: when the whole transcript was gathered;
- tracking command bracket: when the time-error evidence was captured;
- replay `collected_at`: the conservative tracking command start used by the evaluator.

This is a small refactor with operational payoff. It does not add a new TimeState field, a registry, or a credential surface. It only prevents retained capture evidence from becoming artificially fresh because diagnostic commands happened after the tracking sample.

## Severe/wasteful issue corrected

The earlier implementation could spend effort improving sourcestats diagnostics while accidentally letting those diagnostics make the tracking observation look younger. That is the wrong direction: diagnostics may add context, but they must not make the time interval narrower. rev0127 corrects that by anchoring age growth to the earliest safe tracking instant.

## Still open

- The live path is still exercised through a fake `chronyc`, not a real chronyd/chronyc host.
- Wall-clock timestamps in retained captures are still local collector evidence; future live-host work should prefer same-process monotonic aging for immediate evaluation where possible.
- NTS and symmetric-key authentication are not verified.
- UTC is chrony-reported and unqualified; named UTC realization is not proven.
- Leap-smear policy discovery is not implemented.
- RFC 9249 remains a comparison guard, not proof of interoperability.
