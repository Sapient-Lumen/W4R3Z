# Migration map — rev0125 to rev0126

## Operational change

Chrony command capture envelopes now require a fourth role: `sourcestats`, corresponding to `chronyc -n sourcestats`.

Existing rev0125 capture fixtures with only `chronyc_version`, `tracking`, and `sources` should be treated as older replay evidence. For rev0126 validation, retained capture envelopes must include:

1. `chronyc -v`
2. `chronyc -n tracking`
3. `chronyc -n sources`
4. `chronyc -n sourcestats`

## Adapter change

`tools/chrony_adapter.py` accepts an optional `--sourcestats` text file and includes parsed rows in `chrony_observation.sourcestats_summary`.

The P1 policy decision is unchanged. Sourcestats rows are retained for diagnostics and future audit; they do not narrow intervals, improve source posture, or authorize a stronger applicability lane.

## Validation change

`tools/chrony_capture.py --self-test` now runs a fake-live subprocess harness. A temporary executable named `chronyc` is created to prove that the live command runner, capture validation, and replay extraction work without requiring chronyd in the cloud container.

## Core invariant

No new TimeState field was added. The six-field core remains interval, timescale, freshness, regime, source posture, and applicability.
